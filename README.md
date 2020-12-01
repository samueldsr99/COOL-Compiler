# Proyecto 2 Compilacion 3er año

## Inferencia de tipos en COOL

## Estudiantes
* Samuel David Suárez Rodríguez
* Enmanuel Verdesia Suárez

### índice
  - Introducción.
  * Requerimientos.
  * Instalación.
  * Ejecución.
  * Uso.
  * Detalles de la implementación.
  * Limitaciones.

#### Introducción

Los programas en COOL no necesitan especificar las anotaciones de tipo mientras que estas sean inferibles a través del contexto. En este proyecto presentamos un algoritmo para inferir tipos en este lenguaje.

Los tipos de variables inferibles a través del contexto se definen con `AUTO_TYPE`

```typescript
class Main inherits IO {
  main(): AUTO_TYPE {
    let x: AUTO_TYPE <- 3 + 2 in {
      case x of
        y: Int => out_string("Ok");
      esac;
    }
  };
};
```

La salida de nuestro programa será la resultante de un recorrido en el ast con los tipos de los nodos (incluyendo los inferidos), por ejemplo:

```
\__ProgramNode [<class> ... <class>]
  \__ClassDeclarationNode: class Main : IO { <feature> ... <feature> }
    \__FuncDeclarationNode: main() : Int -> <body>
      \__LetNode:  let
       \__VarDeclarationNode: x: Int <-
        \__<expr> PlusNode <expr>
          \__IntegerNode: 3
          \__IntegerNode: 2
        in
          \__BlockNode:
            \__CaseNode: case <expr> of [<case> ... <case>] esac
              \__case
                \__VariableNode: x of
            \__CaseNode: y : Int =>
                  \__CallNode: <obj>.out_string(<expr>, ..., <expr>)
                    \__VariableNode: self
                    \__StringNode: "Ok"
```

donde se sustituyen los tipos `AUTO_TYPE` por el tipo inferido en caso de que se pueda inferir

```typescript
class Main {
  x: AUTO_TYPE;
  y: AUTO_TYPE;
  z: AUTO_TYPE;

  main(): AUTO_TYPE {
    {
      x <- y;
      y <- 1;
    }
  };
};
```

```
\__ProgramNode [<class> ... <class>]
  \__ClassDeclarationNode: class Main  { <feature> ... <feature> }
    \__AttrDeclarationNode: x : Int
    \__AttrDeclarationNode: y : Int
    \__AttrDeclarationNode: z : AUTO_TYPE
    \__FuncDeclarationNode: main() : Int -> <body>
      \__BlockNode:
        \__AssignNode: x <- <expr>
          \__VariableNode: y
        \__AssignNode: y <- <expr>
          \__IntegerNode: 1
```

#### Requerimientos
* python 3
* pip
* streamlit==0.67.1
* streamlit_ace==0.0.4

#### Instalación

Las librerías se pueden instalar automáticamente de la siguiente manera

```bash
pip install -r requirements.txt
```

#### Ejecución

Para iniciar el servidor correr el siguiente comando

```bash
streamlit run index.py
```

#### Uso

Para profundizar en la gramática de COOL puede encontrar la documentación [aquí](data/cool-manual.pdf)

En la interfaz gráfica escribir el código en COOL, `Ctrl-Enter` para analizar.

El resultado será mostrado debajo de la entrada.

#### Detalles de la implementación

##### Análisis léxico
EL proceso de construcción del autómata de expresiones regulares para este lenguaje tiene muchos estados, por eso el tiempo de construcción de este al iniciar el programa tarda 20s aproximadamente.

##### Análisis sintáctico
Se implementó un parser `LR1` pues era suficiente para reconocer la gramática. Sin embargo debido a la lentitud para contruir las tablas `Action` y `GOTO` por el gran número de estados del autómata optamos por construirlas una vez y guardarlas preprocesadas en la clase del parser.

##### Análisis semántico

La inferencia de los tipos se realiza siguiendo las reglas de inferencia de tipos del manual de COOL.

Por ejemplo, una operación de suma se infiere a ser de tipo `Int`

```typescript
class Main {
  suma(x: Int, y: Int): AUTO_TYPE {
    x + y
  };
};
```

##### Detalles de inferencia

El tipo inferido de las expresiones condicionales se define como el padre común mas bajo del árbol de herencia del lenguaje. Por tanto en expresiones recursivas si una rama de esta es `AUTO_TYPE` por conveniencia el tipo de la condicional será `Object`, esto puede afectar el no poder inferir el tipo de retorno de expresiones recursivas dependientes de condiciones cuando una rama de esta llama a la propia función solamente. Solo se puede inferir el tipo si esta llamada viene asociada con algún operador que permita determinar el tipo de la operación. Ver en ejemplo debajo los tipos de `rec` y `fact`

```typescript
class Main {
  rec(n: Int): AUTO_TYPE {
    if n = 0 then 1 else rec(n - 1) fi
  };
  fact(n: Int): AUTO_TYPE {
    if n = 0 then 1 else n * fact(n - 1) fi
  };
};
```

```
\__FuncDeclarationNode: rec(n:Int) : Object -> <body>
\__ConditionalNode: if <expr> then <expr> else <expr> fi
  \__if
    \__<expr> EqualNode <expr>
      \__VariableNode: n
      \__IntegerNode: 0
  \__then
    \__IntegerNode: 1
  \__else
    \__CallNode: <obj>.rec(<expr>, ..., <expr>)
      \__VariableNode: self
      \__<expr> MinusNode <expr>
        \__VariableNode: n
        \__IntegerNode: 1
\__FuncDeclarationNode: fact(n:Int) : Int -> <body>
\__ConditionalNode: if <expr> then <expr> else <expr> fi
  \__if
    \__<expr> EqualNode <expr>
      \__VariableNode: n
      \__IntegerNode: 0
  \__then
    \__IntegerNode: 1
  \__else
    \__<expr> StarNode <expr>
      \__VariableNode: n
      \__CallNode: <obj>.fact(<expr>, ..., <expr>)
        \__VariableNode: self
        \__<expr> MinusNode <expr>
          \__VariableNode: n
          \__IntegerNode: 1
```

Nuestro algoritmo de inferencia solamente infiere los tipos actuales suponiendo que conoce los tipos dependientes de este, esto conlleva a que en una pasada no siempre sea posible determinar todos los tipos, en los casos en que un `AUTO_TYPE` depende de otro `AUTO_TYPE` y el primero se analice antes que el segundo. Para resolver este problema de dependencias nuestro `inferer` notifica si en la pasada hubo alguna inferencia detectada. Lo que hacemos entonces es repetir el algoritmo hasta que en alguna pasada esto no ocurra en ningún momento.

```typescript
class Main {
  x: AUTO_TYPE;
  y: AUTO_TYPE;
  z: AUTO_TYPE;

  main(): AUTO_TYPE {
    {
      x <- y;
      y <- z;
      z <- "Hello";
    }
  };
};
```

```
\__ProgramNode [<class> ... <class>]
  \__ClassDeclarationNode: class Main  { <feature> ... <feature> }
    \__AttrDeclarationNode: x : String
    \__AttrDeclarationNode: y : String
    \__AttrDeclarationNode: z : String
    \__FuncDeclarationNode: main() : String -> <body>
      \__BlockNode:
        \__AssignNode: x <- <expr>
          \__VariableNode: y
        \__AssignNode: y <- <expr>
          \__VariableNode: z
        \__AssignNode: z <- <expr>
          \__StringNode: "Hello"
```

#### Limitaciones

Debido a algunas limitaciones de la definición de la gramática, no es posible deducir el argumento de la declaración de funciones, por tanto se recomienda especificar el tipo de estos argumentos para deducir los tipos dependientes de este.

El Lexer implementado no es capaz de reconocer de forma correcta más de un comentario de la forma **(\*\<texto de comentario\>\*)** en el código. El motivo de esto es que esta implemenetado el mecanismo de reconocimiento de tokens con un autómata finito determinista y este tipo de procesamiento requiere un sistema con memoria, como puede ser un autómata de pila.