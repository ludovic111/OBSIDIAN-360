static int xenon_smc_message(void *msg) {
    const unsigned char *m=msg;
    assert(led_lock); assert(m[0]==0x99 && m[1]==1);
    for(int i=3;i<16;i++) assert(m[i]==0);
    memcpy(last_message,msg,16); sends++; return 0;
}

int main(int argc, char **argv) {
    assert(argc==3);
    int index=atoi(argv[2]);
    if(!strcmp(argv[1],"alloc")) fail_alloc=index;
    else if(!strcmp(argv[1],"led")) fail_led=index;
    else if(!strcmp(argv[1],"driver")) fail_driver=1;
    else if(!strcmp(argv[1],"device")) fail_device=1;
    else if(!strcmp(argv[1],"defer")) ready=0;
    else assert(!strcmp(argv[1],"success"));
    int rc=xenon_led_init();
    if(fail_driver) { assert(rc==-EBUSY && !driver_unregs && !device_live); }
    else if(fail_device) { assert(rc==-ENODEV && driver_unregs==1 && !device_live); }
    else {
        assert(rc==0 && device_live && driver_live);
        if(!ready) assert(probe_result==-EPROBE_DEFER && !sends);
        else if(fail_alloc>=0) assert(probe_result==-ENOMEM);
        else if(fail_led>=0) assert(probe_result==-EIO);
        else {
            assert(probe_result==0 && live_leds==8 && live_memory==9);
            for(int i=0;i<8;i++) {
                registered_leds[i]->brightness_set(registered_leds[i],LED_ON);
                assert(last_message[2]==(1u<<(i+1))-1);
                assert(registered_leds[i]->brightness_get(registered_leds[i])==LED_ON);
            }
            for(int i=0;i<8;i++) {
                registered_leds[i]->brightness_set(registered_leds[i],LED_OFF);
                assert(last_message[2]==(255u & ~((1u<<(i+1))-1)));
                assert(registered_leds[i]->brightness_get(registered_leds[i])==LED_OFF);
            }
        }
        if(probe_result) assert(!live_memory && !live_leds);
        xenon_led_exit(); assert(device_unregs==1 && driver_unregs==1);
    }
    assert(!live_memory && !live_leds && !device_live && !driver_live && !led_lock);
    printf("passed %s %d; sends=%d; no resources remain\n",argv[1],index,sends);
    return 0;
}
