# Máquina de Brookshear

## Descripción

La máquina de Brookshear es una computadora abstracta que implementa un subconjunto del lenguaje de máquina de von Neumann.

## Instrucciones

| Código | Instrucción    | Descripción                                                                                        |
|--------|----------------|----------------------------------------------------------------------------------------------------|
| `1RXY` | `MOV R, [XY] ` | carga el registro R con el valor de la celda de memoria XY                                         |
| `2RXY` | `MOV R, XY   ` | almacena el valor XY en el registro R                                                              |
| `3RXY` | `MOV [XY], R ` | copia el registor R en la celda de memoria XY                                                      |
| `40RS` | `MOV S, R    ` | copia el registro R en el registro S                                                               |
| `5RST` | `ADDI R, S, T` | suma los registros S y T (como complemento a 2) y almacena el resultado en R                       |
| `6RST` | `ADDF R, S, T` | suma los registros S y T (como números de 8 bits con punto flotante) y almacena el resultado en R  |
| `7RST` | `OR R, S, T  ` | realiza un OR entre los registros S y T y almacena el resultado en R                               |
| `8RST` | `AND R, S, T ` | realiza un AND entre los registros S y T y almacena el resultado en R                              |
| `9RST` | `XOR R, S, T ` | realiza un XOR entre los registros S y T y almacena el resultado en R                              |
| `AR0X` | `ROR R, 0    ` | rota X veces el registro R a la derecha                                                            |
| `BRXY` | `CMP R, R0   ` | salta a la dirección XY si el registro R es igual al registro R0                                   |
|        | `JE XY       ` |                                                                                                    |
| `B0XY` | `JMP XY      ` | salta incondicionalmente a la dirección XY                                                         |
| `A000` | `HALT        ` | finaliza la ejecución                                                                              |

## Ejemplo de uso

```bash
uv run brookshear.py assets/program/program.bmc
```

or run it with `--step-by-step` flag to see the execution step

```bash
uv run brookshear.py assets/program/program.bmc --step-by-step
```

or run it with `--debug` flag to see the execution step and the memory state

```bash
uv run brookshear.py assets/program/program.bmc --debug
```
