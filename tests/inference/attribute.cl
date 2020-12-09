class Point {
    x: AUTO_TYPE;
    y: AUTO_TYPE;
    z: AUTO_TYPE;

    init(n: Int, m: Int): AUTO_TYPE {
        {
            z <- x;
            x <- n;
            y <- m;
        }
    };
};
