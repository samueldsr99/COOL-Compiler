class Main {
    fact(x: AUTO_TYPE): AUTO_TYPE {
        if x = 0 then 1 else x * fact(x - 1) fi
    };
};
