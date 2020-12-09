class Main {
    attr: String <- "Hello world";

    func(): AUTO_TYPE {
        let x: AUTO_TYPE <- attr in
            x.length()
    };
};
