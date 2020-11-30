class B{
    s : String <- "Hello";
    g (y:String) : Int {
        y.concat(s)
    };
    f (x:Int) : Int {
        x+1
    };
};

class A inherits B {
    a : Int;
    b : B <- new B;
    f(x:Int) : Int {
        x+a
    };
};
class C inherits A {
    name: String;
    age: Int;
    
    function (x: Bool): Object {
        if x = (not true) then
            name
        else
            {
                age;
                age + 1;
                age + 2;
                name;
                age + age * ~age;
            }
        fi
    };
};

class B inherits A{
    s : String <- "Hello";
    g (y:String) : String {
        y.concat(s)
    };
    f (x:Int) : Int {
        x+1
    };
};

class A inherits B {
    a : Int;
    b : B <- new B;
    f(x:Int) : Int {
        x + a 
    };
};