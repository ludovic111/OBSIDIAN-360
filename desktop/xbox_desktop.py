#!/usr/bin/env python3
"""Small X11 launcher and Xbox joydev-to-XTest bridge, without a compositor."""
import ctypes as C
import json
import math
import os
from pathlib import Path
import signal
import struct
import subprocess
import sys
import time


def stick(value):
    v = min(1.0, abs(value) / 32767)
    return math.copysign(((v - .20) / .80) ** 1.7, value) if v > .20 else 0.0


class X11:
    def __init__(self):
        self.x = C.CDLL('libX11.so.6')
        self.t = C.CDLL('libXtst.so.6')
        self.x.XOpenDisplay.argtypes = [C.c_char_p]
        self.x.XOpenDisplay.restype = C.c_void_p
        self.d = self.x.XOpenDisplay(None)
        if not self.d:
            raise RuntimeError('Cannot open X11 display')
        self.x.XStringToKeysym.argtypes = [C.c_char_p]
        self.x.XStringToKeysym.restype = C.c_ulong
        self.x.XKeysymToKeycode.argtypes = [C.c_void_p, C.c_ulong]
        self.x.XKeysymToKeycode.restype = C.c_ubyte
        self.x.XFlush.argtypes = [C.c_void_p]
        self.x.XGetInputFocus.argtypes = [C.c_void_p, C.POINTER(C.c_ulong), C.POINTER(C.c_int)]
        self.x.XSetInputFocus.argtypes = [C.c_void_p, C.c_ulong, C.c_int, C.c_ulong]
        self.x.XWarpPointer.argtypes = [C.c_void_p, C.c_ulong, C.c_ulong, C.c_int, C.c_int, C.c_uint, C.c_uint, C.c_int, C.c_int]
        self.x.XDefaultRootWindow.argtypes = [C.c_void_p]
        self.x.XDefaultRootWindow.restype = C.c_ulong
        self.t.XTestFakeRelativeMotionEvent.argtypes = [C.c_void_p, C.c_int, C.c_int, C.c_ulong]
        self.t.XTestFakeButtonEvent.argtypes = [C.c_void_p, C.c_uint, C.c_int, C.c_ulong]
        self.t.XTestFakeKeyEvent.argtypes = [C.c_void_p, C.c_uint, C.c_int, C.c_ulong]
        # A closed application may invalidate the keyboard's saved focus window.
        self._error = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_void_p)(lambda d, e: 0)
        self.x.XSetErrorHandler.argtypes = [C.c_void_p]
        self.x.XSetErrorHandler(self._error)

    def flush(self):
        self.x.XFlush(self.d)

    def key(self, name, down):
        code = self.x.XKeysymToKeycode(self.d, self.x.XStringToKeysym(name.encode()))
        if code:
            self.t.XTestFakeKeyEvent(self.d, code, int(down), 0)

    def tap(self, name):
        self.key(name, True)
        self.key(name, False)
        self.flush()

    def button(self, number, down):
        self.t.XTestFakeButtonEvent(self.d, number, int(down), 0)

    def move(self, x, y):
        self.t.XTestFakeRelativeMotionEvent(self.d, x, y, 0)

    def warp(self, x, y):
        self.x.XWarpPointer(self.d, 0, self.x.XDefaultRootWindow(self.d), 0, 0, 0, 0, x, y)
        self.flush()

    def focus(self):
        win, revert = C.c_ulong(), C.c_int()
        self.x.XGetInputFocus(self.d, C.byref(win), C.byref(revert))
        return win.value

    def set_focus(self, win):
        if win > 1:
            self.x.XSetInputFocus(self.d, win, 2, 0)


class Desktop:
    def __init__(self):
        import tkinter as tk
        from tkinter import messagebox
        self.tk, self.messagebox = tk, messagebox
        self.root = tk.Tk(className='XboxLauncher')
        self.root.title('Xbox Linux')
        self.root.configure(bg='#101610')
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f'{min(w-40,1240)}x{min(h-80,640)}+20+20')
        self.root.protocol('WM_DELETE_WINDOW', self.root.withdraw)
        self.x = X11()
        self.fd, self.axes, self.held = None, {}, set()
        self.events = 0
        self.last_event = None
        self.last_time = time.monotonic()
        self.last_scroll = self.last_report = 0
        self.remainder = [0., 0.]
        self.keyboard = None
        self.keyboard_target = 0
        self.shifted = False
        self.selected = 0
        self.buttons = []
        self.state_dir = Path.home()/'.local/state/xbox-desktop'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.label('XBOX  /  LINUX', 31, '#8bdc43').pack(anchor='w', padx=34, pady=(24,4))
        self.label('Votre bureau à la manette', 16, '#cbd6c7').pack(anchor='w', padx=36)
        self.status = self.label('Connexion à la manette…', 12, '#a7b69f')
        self.status.pack(anchor='w', padx=36, pady=(7,12))
        grid = tk.Frame(self.root, bg='#101610')
        grid.pack(fill='both', expand=True, padx=30, pady=4)
        tiles = [
            ('Fichiers', 'Explorer le disque', lambda: self.launch('pcmanfm')),
            ('Terminal', 'Ouvrir une console', lambda: self.launch('xterm','-fa','DejaVu Sans Mono','-fs','13')),
            ('Clavier', 'Y dans une application', self.toggle_keyboard),
            ('Commandes', 'Les boutons de la manette', self.help),
            ('Système', 'Mémoire et stockage', self.info),
            ('Éteindre', 'Arrêter proprement la Xbox', self.poweroff),
        ]
        for i, (title, desc, action) in enumerate(tiles):
            b=tk.Button(grid,text=f'{title}\n{desc}',command=action,font=('DejaVu Sans',17),
                bg='#202d20',fg='#eef4e9',activebackground='#39592b',activeforeground='white',
                relief='flat',bd=0,highlightthickness=3,highlightbackground='#202d20',
                highlightcolor='#8bdc43',padx=12,pady=16,cursor='hand2',takefocus=True)
            b.grid(row=i//3,column=i%3,sticky='nsew',padx=7,pady=7)
            self.buttons.append(b)
        for c in range(3): grid.columnconfigure(c,weight=1,uniform='tiles')
        for r in range(2): grid.rowconfigure(r,weight=1,uniform='rows')
        self.label('STICK GAUCHE  Pointeur     A  Clic     X  Clic droit     B  Retour',12,'#cbd6c7').pack(pady=(16,4))
        self.label('STICK DROIT  Défiler     Y  Clavier     START  Accueil     RB  Entrée',12,'#a7b69f').pack(pady=(0,18))
        for key, delta in [('Left',-1),('Right',1),('Up',-3),('Down',3)]:
            self.root.bind('<'+key+'>',lambda e,d=delta:self.select(d))
        self.root.bind('<Return>',lambda e:self.buttons[self.selected].invoke())
        self.root.bind('<Escape>',lambda e:self.root.withdraw())
        self.root.after(250,self.home)
        self.root.after(30,self.tick)
        signal.signal(signal.SIGTERM,lambda *a:self.stop())
        signal.signal(signal.SIGUSR1,lambda *a:self.root.after(0,self.toggle_keyboard))

    def label(self, text, size, color):
        return self.tk.Label(self.root,text=text,font=('DejaVu Sans',size),bg='#101610',fg=color)

    def select(self, delta):
        self.selected=(self.selected+delta)%len(self.buttons)
        b=self.buttons[self.selected]
        b.focus_set()
        self.x.warp(b.winfo_rootx()+b.winfo_width()//2,b.winfo_rooty()+b.winfo_height()//2)
        return 'break'

    def home(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.after(50,lambda:self.select(0))

    def launch(self,*cmd):
        subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    def help(self):
        self.messagebox.showinfo('Commandes','Stick gauche : pointeur\nA : clic / glisser\nX : clic droit\nB : Échap / retour\nY : clavier à l’écran\nStick droit : défilement\nCroix : flèches\nLB : effacer\nRB : Entrée\nBACK : Tabulation\nSTART : revenir à cet accueil',parent=self.root)

    def info(self):
        mem={l.split(':')[0]:int(l.split()[1]) for l in Path('/proc/meminfo').read_text().splitlines()}
        s=os.statvfs('/')
        self.messagebox.showinfo('Système',f'ArchPOWER · Xbox 360\n\nRAM disponible : {mem["MemAvailable"]//1024} Mo\nSwap : {mem["SwapTotal"]//1024} Mo\nDisque libre : {s.f_bavail*s.f_frsize/2**30:.1f} Gio\n\nBureau léger, rendu sans effets 3D.',parent=self.root)

    def poweroff(self):
        if self.messagebox.askyesno('Éteindre','Éteindre la Xbox maintenant ?',default='no',parent=self.root):
            r=subprocess.run(['systemctl','poweroff'],capture_output=True,text=True)
            if r.returncode:self.messagebox.showerror('Arrêt',r.stderr,parent=self.root)

    def type_key(self, symbol):
        self.x.set_focus(self.keyboard_target)
        if self.shifted:self.x.key('Shift_L',True)
        self.x.tap(symbol)
        if self.shifted:self.x.key('Shift_L',False)
        self.x.flush()

    def toggle_keyboard(self):
        if self.keyboard is not None:
            self.keyboard.destroy(); self.keyboard=None
            return
        self.keyboard_target=self.x.focus()
        k=self.tk.Toplevel(self.root)
        self.keyboard=k
        k.overrideredirect(True)
        k.configure(bg='#111b12')
        w=min(self.root.winfo_screenwidth()-30,1120)
        k.geometry(f'{w}x290+{(self.root.winfo_screenwidth()-w)//2}+{self.root.winfo_screenheight()-310}')
        k.attributes('-topmost',True)
        rows=[list('1234567890'),list('azertyuiop'),list('qsdfghjklm'),list('wxcvbn')+['comma','period','minus','slash']]
        for row in rows:
            f=self.tk.Frame(k,bg='#111b12'); f.pack(fill='both',expand=True,padx=6,pady=3)
            for key in row:
                display={'comma':',','period':'.','minus':'-','slash':'/'}.get(key,key)
                self.tk.Button(f,text=display,font=('DejaVu Sans',16),takefocus=False,
                    bg='#2a3a28',fg='white',activebackground='#50733a',relief='flat',
                    command=lambda v=key:self.type_key(v)).pack(side='left',fill='both',expand=True,padx=2)
        f=self.tk.Frame(k,bg='#111b12'); f.pack(fill='both',expand=True,padx=6,pady=3)
        for text,key in [('Tab','Tab'),('Espace','space'),('Effacer','BackSpace'),('Entrée','Return')]:
            self.tk.Button(f,text=text,command=lambda v=key:self.type_key(v),takefocus=False,
                font=('DejaVu Sans',13),bg='#37502b',fg='white',relief='flat').pack(side='left',fill='both',expand=True,padx=2)
        self.tk.Button(f,text='Maj ⇧',command=lambda:setattr(self,'shifted',not self.shifted),takefocus=False,
            font=('DejaVu Sans',13),bg='#37502b',fg='white',relief='flat').pack(side='left',fill='both',expand=True,padx=2)
        self.tk.Button(f,text='Fermer · Y',command=self.toggle_keyboard,takefocus=False,
            font=('DejaVu Sans',13),bg='#50733a',fg='white',relief='flat').pack(side='left',fill='both',expand=True,padx=2)
        self.root.after(60,lambda:self.x.set_focus(self.keyboard_target))

    def event(self, typ, num, val):
        initial=bool(typ&128); typ&=127
        if typ==2:
            old=self.axes.get(num,0); self.axes[num]=val
            if num in (6,7) and not initial:
                pair=('Left','Right') if num==6 else ('Up','Down')
                if old:self.x.key(pair[old>0],False); self.held.discard(('key',pair[old>0]))
                if val:self.x.key(pair[val>0],True); self.held.add(('key',pair[val>0]))
        elif typ==1 and not initial:
            if num in (0,2):
                button=1 if num==0 else 3
                self.x.button(button,val)
                (self.held.add if val else self.held.discard)(('button',button))
            elif num in (1,4,5,6):
                name={1:'Escape',4:'BackSpace',5:'Return',6:'Tab'}[num]
                self.x.key(name,val)
                (self.held.add if val else self.held.discard)(('key',name))
            elif val and num==3:self.toggle_keyboard()
            elif val and num in (7,8):self.home()
        if not initial:
            self.events+=1; self.last_event={'type':typ,'number':num,'value':val}

    def release(self):
        for kind,value in self.held:
            (self.x.key if kind=='key' else self.x.button)(value,False)
        self.held.clear(); self.axes.clear(); self.x.flush()

    def tick(self):
        now=time.monotonic(); dt=min(.05,now-self.last_time); self.last_time=now
        try:
            if self.fd is None:
                self.fd=os.open('/dev/input/js0',os.O_RDONLY|os.O_NONBLOCK)
                self.status.config(text='MANETTE DÉTECTÉE  ·  Stick pour déplacer le pointeur')
            while True:
                try: data=os.read(self.fd,512)
                except BlockingIOError:break
                if not data:raise OSError('Joystick disconnected')
                for _,val,typ,num in struct.iter_unpack('=IhBB',data):self.event(typ,num,val)
        except OSError:
            if self.fd is not None:os.close(self.fd); self.fd=None; self.release()
            self.status.config(text='Allumez la manette Xbox 360')
        delta=[]
        for n in (0,1):
            value=stick(self.axes.get(n,0))*780*dt+self.remainder[n]
            delta.append(int(value)); self.remainder[n]=value-int(value)
        if any(delta):self.x.move(*delta)
        scroll=stick(self.axes.get(4,0))
        if abs(scroll)>.15 and now-self.last_scroll>.12:
            b=5 if scroll>0 else 4
            self.x.button(b,True); self.x.button(b,False); self.last_scroll=now
        self.x.flush()
        if now-self.last_report>2:
            (self.state_dir/'input.json').write_text(json.dumps({'device_open':self.fd is not None,'events':self.events,'last_event':self.last_event}))
            self.last_report=now
        self.root.after(30,self.tick)

    def stop(self):
        self.release()
        self.root.destroy()


if __name__=='__main__':
    if '--self-test' in sys.argv:
        assert struct.calcsize('=IhBB')==8
        assert stick(0)==stick(4000)==0
        assert stick(32767)==1 and stick(-32767)==-1
        assert struct.unpack('=IhBB',struct.pack('=IhBB',7,-123,2,1))==(7,-123,2,1)
        print('controller decoding and deadzone: OK')
    else:
        app=Desktop()
        app.root.mainloop()
