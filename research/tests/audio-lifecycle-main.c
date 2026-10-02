/* Original test entrypoint, MIT. One process per injected failure. */
int main(int argc,char **argv) {
    if(argc!=3)return 2;
    fault=argv[1];int candidate=atoi(argv[2]);
    struct pci_dev pci={.irq=12};struct pci_device_id pci_id={0};
    int code=snd_xenon_probe(&pci,&pci_id);
    int want=0;
    if(fail("card"))want=-ENOSPC;
    else if(fail("pci_enable")||fail("regions")||(!candidate&&fail("irq")))want=-EBUSY;
    else if(fail("chip_alloc")||fail("ioremap")||fail("dma_alloc")||fail("pcm0")||fail("pcm1")||(!candidate&&fail("lowlevel")))want=-ENOMEM;
    else if(fail("bar_type")||fail("bar_short"))want=-ENODEV;
    else if(fail("dma_mask")||fail("smc_send")||fail("register"))want=-EIO;
    else if(fail("smc_ready"))want=-EPROBE_DEFER;
    else if(fail("smc_busy"))want=-EBUSY;
    else if(fail("smc_timeout"))want=-ETIMEDOUT;
    else if(fail("buffer0")||fail("buffer1"))want=-ENOMEM;
    CHECK(code==want);
    if(code==0) {
        CHECK(pci.data);
        if(fail("active_remove")) {
            struct snd_card *card=pci.data;struct snd_xenon *chip=card->private_data;
            chip->devices[0].state=3;chip->timer_in_use=1;chip->timer.pending=1;
            active_dma=active_timer=1;
        }
        snd_xenon_remove(&pci);
    }
    CHECK(!pci.data);CHECK(!live_allocs);CHECK(!enabled);CHECK(!regions);
    CHECK(!mapped);CHECK(!irq_owned);CHECK(!dma_owned);CHECK(!bus_master);CHECK(!locked);
    printf("%s: code=%d all resources released; smc_calls=%d\n",fault,code,smc_calls);
    return 0;
}
