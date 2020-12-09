class Main {
    infer_int(): AUTO_TYPE {
        (new A).int()
    };
    infer_string(): AUTO_TYPE {
        (new A).string()
    };
};

class A {
    int(): AUTO_TYPE {
        new Int
    };
    string(): AUTO_TYPE {
        new String
    };
};
