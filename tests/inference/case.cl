class C {
    
};

class B inherits C {
};

class A inherits C {
};

class Main inherits IO {
    func(): AUTO_TYPE {
        case 1 + 1 of
            a: A => new A;
            b: B => new B;
        esac
    };
};
