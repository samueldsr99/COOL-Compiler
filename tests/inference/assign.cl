class Main {
    base: AUTO_TYPE <- 1 + 1;
    
    f1(): AUTO_TYPE {
        f2()
    };
    
    f2(): AUTO_TYPE {
        f3()
    };
    
    f3(): AUTO_TYPE {
        f4()
    };
    
    f4(): AUTO_TYPE {
        base
    };
};

