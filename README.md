# Proyecto 2 Compilacion 3er año

## Inferencia de tipos en COOL

### índice
  - Introducción.
  * Requerimientos.
  * Instalación.
  * Uso.
  * Detalles de la implementación.
  * TODO.

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
class Main{
  suma(x: Int, y: Int): AUTO_TYPE {
    {
      z <- x + y;
      z;
    }
  };
};
```

```

```
