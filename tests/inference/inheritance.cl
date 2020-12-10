class A inherits B {
    set_value(new_value: Int): AUTO_TYPE {
        x <- new_value
    };
};

class B inherits C {};

class C inherits D {};

class D inherits E {};

class E {
    x: AUTO_TYPE;
};
