"""Author presentation content from the reviewed code and archived audit."""
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
sys.path.insert(0,str(PROJECT/'backend/src'))
from area_lab.infrastructure.designs import DESIGNS

audit=json.loads((HERE/'auditoria_evidencias.json').read_text())
root=PROJECT/'docs/validation/dpu-matrix-20261018'
reports={(r['design_id'],r['technology_id']):r for r in audit['cases']}
slides=[]

def add(title,section,kind,notes,refs=(),local='',**data):
    slides.append(dict(title=title,section=section,type=kind,notes=notes,refs=list(refs),local=local,**data))

add('Del VHDL al área ASIC: qué medimos y qué podemos demostrar','Revisión técnica · GIRA','cover',
    'Esta presentación describe el programa tal como existe al19 de octubre de2026. Su objetivo es someter el método y las evidencias a revisión, no defender una certeza absoluta. Se volvió a auditar el archivo conservado de30 combinaciones, sin ejecutar nuevas síntesis. Los diagramas representan módulos y comandos reales. El argumento defendible es que se obtiene una estimación prelayout de área de celdas de una implementación registrada concreta. La corrección física final, la equivalencia exhaustiva y la precisión matemática de todas las familias siguen fuera de lo demostrado.',
    subtitle='Código, arquitectura, bibliotecas, comandos y evidencia verificable',
    chips=['11 DPU integradas','3 bibliotecas typical','30 casos documentados'],
    takeaway='Una medición delimitada y trazable; una conclusión con límites explícitos.')

add('La base metodológica es defendible; la validación sigue siendo parcial','01 · Dictamen de la revisión','cards',
    'La auditoría realizada hoy recalcula sumas y hashes de los archivos conservados. No es una nueva ejecución de GHDL o Yosys. Los30 casos corresponden a diez diseños por tres tecnologías. LNS16 figura en el catálogo, pero no tiene tres reportes completos. Las pruebas ligeras de software pasaron hoy:20 backend y42 frontend. Es razonable aceptar la metodología como estudio exploratorio de área de celdas, condicionando la publicación de conclusiones fuertes a completar la cadena de artefactos y delimitar la exactitud funcional.',
    local='auditoria_evidencias.json · pruebas ligeras 19/10/2026',
    cards=[['Coherencia comprobada','30 reportes: conteos, áreas, hashes, vectores y logs compatibles.'],['Pendientes reales','LNS16: tres mapeos sin cerrar. No existe certificación física ni prueba formal.'],['Decisión propuesta','Aceptar el método para área de celdas y cerrar las brechas antes de ampliar las afirmaciones.']],
    takeaway='No se concluye que todo el sistema esté validado exhaustivamente.')

add('La magnitud de interés es la suma de áreas de las celdas mapeadas','02 · Alcance','scope',
    'Área de celdas significa sumar las áreas nominales de los tipos de celdas que aparecen en la netlist. Se incluyen los FF del wrapper registrado. Las conexiones lógicas son indispensables para definir el circuito, aunque se excluya el área física de los cables. No se realiza placement ni routing; por tanto no existe evidencia sobre utilización, congestión, die o cierre temporal. El resultado se refiere a esta netlist bajo esta biblioteca y esta política de mapeo, no al menor circuito posible ni al tamaño final de un chip.',
    refs=['F04','F06'],local='infrastructure/liberty.py · summarize_netlist()',
    formula='A celdas = Σ [ número de instancias × área de su tipo ]',
    left=['Lógica combinacional','Flip-flops del wrapper','ROM reducida a lógica'],
    right=['Área de cables y routing','Core, pads, die y clock tree','Potencia, frecuencia y STA'],
    takeaway='El área física de las conexiones se excluye; las conexiones lógicas se conservan.')

add('El objeto medido son once DPU registradas ya existentes','03 · Código de origen','table',
    'Los perfiles se obtuvieron del subproyecto DPU_Performance_Area_Comparison. No son nuevas arquitecturas inventadas para la presentación. Cada top tiene su wrapper original y anchos concretos. DPU designa aquí cuatro productos y acumulación, con las particularidades de cada implementación. La aplicación actual no integra octets ni TCU completas. La descripción de la jerarquía más amplia del repositorio no debe confundirse con el alcance realmente ejecutable.',
    local='infrastructure/designs.py · assets/manifest.json',
    headers=['Perfil','A/B','C/R','Registros declarados','Particularidad'],
    rows=[[d.id,str(d.operand_bits),str(d.result_bits),str(d.declared_register_bits),
           'es=1; nombre histórico _0' if d.id=='posit16' else 'es=0' if d.id=='posit8' else 'es=2' if d.id=='posit32' else 'ROM de corrección' if d.id=='lns16' else 'Referencia entera' if d.family=='integer' else 'FMA del RTL' if d.family=='floating' else 'MAC del RTL'] for d in DESIGNS],
    widths=[2.15,.8,.8,2.8,4.7],dense=True,
    takeaway='Los bits declarados no se convierten automáticamente en un número fijo de FF mapeados.')

add('El wrapper establece la frontera de área y la latencia observable','04 · Circuito medido','flow',
    'En INT8/16 hay ocho operandos de8bits y un acumulador de16bits registrados:80bits de entrada. Se añade un registro de salida de16bits, para96bits declarados. La lógica de la DPU se conserva. Los valores de96FF en INT8 y192FF en INT16 son controles estrictos del perfil; otras familias permiten optimizaciones de bits no observables, siempre que quede estado y pase la comparación funcional. Dos flancos permiten capturar entradas y después la salida correspondiente, sin que ello imponga una frecuencia realizable.',
    local='assets/rtl/int8_16/INT8_16_DPU_perf_top.vhd · validation.py',
    steps=[['80 bits de entrada','A0…A3, B0…B3 y C0'],['DPU combinacional','4 productos + acumulación'],['16 bits de salida','R_out registrado']],
    formula='INT8/16: 8 × 8 + 2 × 16 = 96 bits declarados',
    takeaway='Se mide la DPU con su wrapper; no solo la expresión aritmética.')

add('Diseño y tecnología se eligen antes de crear el trabajo','05 · Selección del experimento','flow',
    'El usuario selecciona un design_id que ya determina formato, top, anchos, archivos y biblioteca VHDL. No se cambia un parámetro de formato dentro del mismo hardware después de sintetizar. El technology_id selecciona un Liberty específico. La API acepta únicamente IDs enumerados y rechaza campos arbitrarios; por tanto el navegador no envía un comando de shell ni una ruta para ejecutar. La solicitud crea un UUID y devuelve202. Los resultados llegan por consulta posterior.',
    refs=['F13','F14'],local='ExperimentForm.tsx · api/schemas.py · ExperimentService.submit()',
    steps=[['Diseño / formato','Ejemplo: int8_16'],['Tecnología / Liberty','Ejemplo: nangate45'],['POST /experiments','UUID + estado queued']],
    code='POST /api/v1/experiments\n{"design_id":"int8_16","technology_id":"nangate45"}',
    takeaway='Un experimento combina un top y un Liberty; no ejecuta todo el barrido automáticamente.')

add('Las tres bibliotecas activas corresponden a condiciones typical','06 · Tecnología y condiciones','table',
    'Se contrastaron el catálogo, el manifiesto de assets y los campos nominales de cada archivo. Los tres snapshots son copias idénticas a los originales por SHA-256. En IHP se usa1.20V; la otra biblioteca typical de1.50V no es la seleccionada. Nangate45 usa el paquete base, Front_End/Liberty/NLDM, no Low_Power ni un binario .db. Las condiciones nominales son distintas entre nodos: same typical no significa mismo proceso ni misma tensión física.',
    refs=['F08','F09','F10'],local='infrastructure/catalog.py · scripts/prepare_assets.py',
    headers=['ID / nodo','Voltaje','Temperatura','Archivo Liberty activo'],
    rows=[['ihp130 · 130 nm','1,20 V','25 °C','sg13g2_stdcell_typ_1p20V_25C.lib'],['nangate45 · 45 nm','1,10 V','25 °C','NangateOpenCellLibrary_typical.lib'],['nangate15 · 15 nm','0,80 V','25 °C','NanGate_15nm_OCL_typical_conditional_nldm.lib']],
    widths=[2.1,1.35,1.55,6.25],
    takeaway='Sí: todos los experimentos documentados usan los typical seleccionados.')

add('Un proceso real y un kit predictivo sostienen conclusiones distintas','07 · Qué representa cada biblioteca','cards',
    'La fuente de una biblioteca importa tanto como su nodo. IHP130 está vinculado al proceso SG13G2, pero el PDK abierto se publica como preview y el programa no hace un tape-out. FreePDK45 y FreePDK15 son plataformas genéricas predictivas de investigación, apropiadas para estudiar implementaciones bajo esas reglas y celdas. No son una promesa de área de un proceso comercial arbitrario llamado45 o15nm. El nombre de nodo tampoco permite extrapolar por el cuadrado de la longitud.',
    refs=['F08','F09','F10'],
    cards=[['IHP SG13G2 · 130 nm','Deriva de un proceso fabricado. El PDK abierto figura como preview.'],['Nangate / FreePDK45','Biblioteca de referencia sobre un proceso genérico predictivo de investigación.'],['Nangate / FreePDK15','Referencia predictiva FinFET; no equivale a cualquier nodo comercial de 15 nm.']],
    takeaway='La conclusión válida nombra la biblioteca exacta, su corner y su procedencia.')

add('El inventario suministrado es mayor que el catálogo habilitado','08 · Matriz experimental','cards',
    'El Excel elaborado previamente separa33combinaciones habilitadas de121propuestas. Existen14Liberty NLDM base: seisIHP, cincoNangate45 y tresNangate15. Solo tres son los snapshots activos. Los otros once requieren crear perfiles y revisar simulación y mapeo. Hay53archivos .lib de inventario, excluyendo metadatos Apple. CCS/ECSM y Low_Power se listan, pero no se cuentan automáticamente como estudios físicos independientes ni se mezclan con el paquete base.',
    local='docs/experimentos/Plan_experimentos_DPU_ASIC_2026-10-19.xlsx',
    cards=[['33 actuales','11 diseños × 3 Liberty activos; todos typical.'],['121 propuestas','11 diseños × 11 Liberty NLDM base adicionales, sin integrar.'],['53 archivos inventariados','NLDM, CCS, ECSM y funcionales; se excluyen ._* de Apple.']],
    takeaway='Tener un archivo en syn_libraries no lo habilita automáticamente en la API.')

add('La aplicación separa decisiones de dominio de herramientas externas','09 · Arquitectura limpia','architecture',
    'ExperimentService depende de dos protocolos del dominio: ExperimentRepository y SynthesisGateway. Los adaptadores concretos SQLiteExperimentRepository y GhdlYosysSynthesis implementan esas fronteras. create_app es la raíz de composición. FastAPI expone el caso de uso; React consume contratos JSON; el dominio no importa FastAPI ni SQLite. El adaptador de síntesis orquesta herramientas y recoge reportes. Esta separación mejora la trazabilidad y permite probar fallos con un gateway simulado, pero por sí sola no demuestra la validez científica del área.',
    local='domain/ports.py · application/services.py · main.py',
    takeaway='El frontend representa datos; el cálculo está en los adaptadores EDA y Liberty.')

add('Un solo contenedor reúne API, frontend compilado y herramientas EDA','10 · Ejecución y persistencia','flow',
    'La construcción tiene tres etapas: Node compila React/Vite; una etapa descarga la suite EDA fijada y verifica su SHA; el runtime PythonTrixie recibe ambos resultados. FastAPI sirve el frontend de producción. SQLite está embebido y no hay un servidor PostgreSQL adicional. El volumen /app/data conserva la base y las carpetas runs. Vite no es un servicio extra de producción. El acceso a Docker quedó bloqueado en esta sesión; no se usa la existencia del Dockerfile como evidencia de un build reciente exitoso.',
    refs=['F12','F15','F16','F17'],local='Dockerfile · compose.yaml · main.py',
    steps=[['Node + Vite','Construye frontend/dist'],['OSS CAD Suite','Release y SHA fijados'],['Python + FastAPI','Sirve UI, API y worker']],
    formula='Volumen /app/data = experiments.sqlite3 + runs/<UUID>/',
    takeaway='Un contenedor; SQLite embebido; un worker EDA. No se necesita PostgreSQL para este alcance.')

add('El trabajo avanza por estados y publica el área al terminar los controles','11 · Ciclo de vida','flow',
    'La cola admite cuatro pendientes y un worker ejecuta trabajos mediante asyncio.to_thread, de modo que las herramientas no bloquean el loopHTTP. Los estados de progreso van de preparing a reporting. Un error genera failed y conserva el diagnóstico. Al reiniciar, los registros queued o running se marcan interrupted y no se reanudan automáticamente. La API de CSV exige succeeded. Las pruebas de aceptación de API usan un gateway falso para probar el flujo de estados; no se cuentan como síntesis reales.',
    local='ExperimentService.work() / _execute() · sqlite_repository.py · api/routes.py',
    steps=[['queued','UUID persistido'],['running','Validación + síntesis'],['succeeded / failed','Reporte o diagnóstico']],
    code='preparing → analyzing → validating_rtl → converting\n→ mapping → checking → validating_mapped → reporting',
    takeaway='Un exit code correcto de una herramienta no basta para publicar un reporte válido.')

add('El perfil del diseño evita seleccionar archivos o anchos a mano','12 · Datos que gobiernan el pipeline','code',
    'El perfil contiene todos los parámetros variables que el adaptador necesita. El mismo registro también gobierna la preparación de assets, reduciendo el riesgo de divergencia. Estos son campos reales del perfil INT8, resumidos para la diapositiva. source_files se mantiene ordenado y relativo a assets. Un design_id también define su referencia funcional. No hay un selector libre de nombres de entidad, ni se infiere el formato por analizar un archivo con un patrón genérico.',
    local='infrastructure/designs.py · domain/models.py',
    code='id="int8_16"\ntop="INT8_16_DPU_perf_top"\nlibrary="int8_16_lib"\noperand_bits=8; result_bits=16\ndeclared_register_bits=96\nreference="signed_dot_modulo"\nexpected_flip_flops=96\ncompilation="files"',
    explanation='Un único perfil determina:\n\n• El RTL y el wrapper.\n• El orden de análisis.\n• Los anchos del testbench.\n• El control de registros.\n• La referencia funcional.',
    takeaway='El programa mide variantes revisadas del repositorio; no cualquier VHDL arbitrario.')

add('Cada ejecución conserva la identidad de sus entradas','13 · Procedencia y hashes','flow',
    'prepare_assets copia bytes del subrepositorio y Liberty originales sin reescribirlos. El manifiesto de assets incluye commit y hashes; el propio manifiesto advierte que el commit no sustituye al hash si hay cambios locales. Cada run vuelve a copiar los archivos a sources y el Liberty a cells.lib. El manifiesto del experimento añade versiones y hashes de estímulos y resultados. Un SHA identifica bytes y detecta diferencias con una referencia retenida; no constituye firma de una tercera parte ni prueba de que nadie haya modificado toda la cadena.',
    local='prepare_assets.py · synthesis.py · manifest.json',
    steps=[['Originales','RTL + Liberty suministrados'],['assets/','Snapshots y SHA-256'],['runs/<UUID>/','Entradas y manifiesto del caso']],
    formula='Auditoría actual: 44 archivos originales ↔ snapshots, hashes coincidentes',
    takeaway='La trazabilidad explica qué se midió; no prueba por sí sola que el RTL sea correcto.')

add('GHDL analiza las dependencias y el wrapper en bibliotecas separadas','14 · Preparación VHDL','code',
    'GHDL es una herramienta de análisis, elaboración y simulación VHDL que también ofrece síntesis. En este programa es un ejecutable, no una librería Python ni un servidor aparte. El adaptador ejecuta el análisis de fuentes en la biblioteca del perfil y el wrapper en work, de acuerdo con sus declaraciones library/use. Las opciones std=08, fsynopsys y fexplicit son las realmente usadas para este RTL. Una mala dependencia falla antes de medir área. La conversión de síntesis es otra llamada posterior.',
    refs=['F01'],local='infrastructure/vhdl.py · synthesis.py',
    code='ghdl -a --std=08 -fsynopsys -fexplicit \\\n  --work=int8_16_lib <fuentes ordenadas>\n\nghdl -a --std=08 -fsynopsys -fexplicit \\\n  sources/rtl/int8_16/INT8_16_DPU_perf_top.vhd',
    explanation='Primero: operadores y DPU.\n\nDespués: wrapper en work.\n\nCada caso usa su carpeta y sus bibliotecas compiladas.\n\nLas rutas completas quedan en run.log.',
    takeaway='Los comandos se muestran para INT8; las fuentes se sustituyen por las del perfil elegido.')

add('Posit16 y Posit32 requieren resolver helpers duplicados sin alterar su RTL','15 · Caso especial de compilación','flow',
    'El backend LLVM de GHDL genera objetos por archivo. Los archivos FloPoCo de suma y multiplicación repiten helpers, lo que producía símbolos duplicados al enlazar la simulación nativa. La infraestructura usa el parser ghdl--chop para separar unidades. Si dos unidades con el mismo nombre son idénticas byte a byte, se conserva una copia; si difieren, se falla. No se usa una opción de linker que oculte conflictos y los snapshots originales se conservan. Las seis ejecuciones Posit16/32 completas documentan esta política y sus unidades derivadas.',
    local='infrastructure/vhdl.py · compilation/*.vhdl · manifiestos Posit16/32',
    steps=[['Suma + multiplicación','Contienen helpers repetidos'],['ghdl --chop','Unidades con nombre y hash'],['Comparar y analizar','Solo reutilizar bytes idénticos']],
    formula='Mismo nombre + contenido distinto → PipelineFailure',
    takeaway='Posit16 usa es=1 según sus operadores, aunque sus archivos se llamen posit16_0_*.')

add('El RTL produce la referencia y los enteros tienen un oráculo adicional','16 · Estímulos y significado de la prueba','cards',
    'write_vectors genera256estímulos con semilla20261005. Se incluyen extremos, signos, actividad por lane y palabras aleatorias. GHDL debe producir256resultados definidos. Para INT8 e INT16 Python comprueba además un producto punto con signo, reducido módulo2^bitsR. Para FXP, FP, Posit y LNS, el esperado sale del RTL suministrado: la prueba verifica preservación del comportamiento, no demuestra que la aritmética original coincida con una matemática ideal. Los formatos no se reinterpretan usando floats de Python.',
    local='validation.py · write_vectors() / check_rtl_results()',
    cards=[['Casos reproducibles','256 estímulos por perfil. Semilla 20261005, casos dirigidos y palabras crudas.'],['INT8 / INT16','Oráculo independiente de producto punto firmado módulo 2^bits(R).'],['FXP / FP / Posit / LNS','Oráculo del propio RTL. Comparación bit a bit; precisión matemática no evaluada.']],
    takeaway='La prueba adicional de enteros no se extiende automáticamente a las otras aritméticas.')

add('Dos flancos por estímulo respetan el wrapper registrado','17 · Simulación original','flow',
    'El testbench asigna los operandos, genera un primer flanco para capturar entradas y un segundo para registrar el resultado. Después rechaza salidas indefinidas y las escribe como hexadecimal. Los pequeños waits garantizan el orden de eventos de simulación; no son una restricción de síntesis y no demuestran que la lógica alcance50MHz. La simulación mapped utiliza la misma secuencia lógica de flancos, pero no hay SDF ni modelos de retardos de celda.',
    refs=['F07'],local='validation.py · VHDL_TESTBENCH / VERILOG_TESTBENCH',
    steps=[['Asignar A/B/C','Entradas estables'],['Flanco 1','Registrar entradas'],['Flanco 2 + muestreo','Registrar y comprobar R']],
    code='assert not is_x(r) ... severity failure;\nVALIDATION_OK 256\nrtl-results.txt → vectors.txt (entradas + esperado)',
    takeaway='Los tiempos del testbench ordenan eventos; no constituyen STA ni cierre temporal.')

add('GHDL genera Verilog para que Yosys pueda sintetizar el diseño','18 · Conversión','code',
    'El programa usa el frontend standalone de GHDL. No invoca un plugin de GHDL dentro de Yosys. --synth elabora el top y --out=verilog escribe design.v. La documentación de GHDL declara experimental su motor de síntesis; por eso la conversión no se acepta solo porque terminó con código0. La netlist final se compara con el RTL mediante simulación. No se calcula área en esta fase y el tamaño de design.v en disco no se usa como área física.',
    refs=['F01'],local='synthesis.py · fase converting',
    code='ghdl --synth --std=08 \\\n  -fsynopsys -fexplicit \\\n  --out=verilog INT8_16_DPU_perf_top\n\n# stdout se guarda en design.v',
    explanation='Entrada: VHDL analizado.\n\nSalida: Verilog estructural.\n\nTodavía no hay celdas de la biblioteca objetivo.\n\nLa preservación se comprueba después del mapeo.',
    takeaway='La conversión es una transformación del diseño; requiere controles posteriores.')

add('El script de Yosys hace explícita la política de síntesis y mapeo','19 · Comandos reales','code',
    'Este fragmento reproduce el script generado para INT8. read_liberty-lib declara tipos de celdas como cajas negras para el mapeo; synth aplana y sintetiza, posponiendo ABC mediante-noabc. Después se mapean los FF y la lógica con la misma biblioteca. Se retira únicamente scopeinfo, un metadato, no hardware desconocido. check-assert añade un control estructural y write_json/write_verilog guardan la implementación. stat usa el mismo Liberty. No hay objetivo de frecuencia, lectura SDC, PnR o comando formal.',
    refs=['F02','F03','F04','F05'],local='synthesis.py · synth.ys',
    code='read_liberty -lib cells.lib\nread_verilog design.v\nhierarchy -check -top INT8_16_DPU_perf_top\nsynth -top INT8_16_DPU_perf_top -flatten -noabc\ndfflibmap -liberty cells.lib\nabc -liberty cells.lib\ndelete t:$scopeinfo\nclean\ncheck -assert\nwrite_json mapped.json\nwrite_verilog -noattr mapped.v\ntee -o stat.json stat -liberty cells.lib -json',
    explanation='Una política común para comparar tecnologías.\n\nSin frecuencia objetivo.\n\nSin memoria SRAM mapeada.\n\nLos scripts y versiones del caso forman parte de la evidencia.',
    takeaway='check -assert revisa estructura; no prueba equivalencia funcional.',compact=True)

add('dfflibmap y ABC eligen celdas tecnológicas para funciones diferentes','20 · Mapeo tecnológico','flow',
    'Yosys transforma el diseño en operadores y lógica genérica. dfflibmap resuelve los elementos secuenciales soportados por la biblioteca, con las inversiones o lógica que resulten necesarias. ABC realiza optimización y mapeo combinacional dentro de Yosys; no es un servicio separado del sistema. La biblioteca fija qué puertas y tamaños de drive están disponibles. El resultado depende de heurísticas y del catálogo; la ausencia de un objetivo temporal explícito no demuestra un óptimo global de área.',
    refs=['F02','F06'],local='synth.ys · logs de ABC en run.log.gz',
    steps=[['Lógica genérica','Operadores, puertas y FF'],['dfflibmap','Estado → FF Liberty'],['ABC -liberty','Lógica → puertas Liberty']],
    formula='Netlist mapeada = instancias concretas + conexiones lógicas',
    takeaway='Se mide el resultado de esa política de mapeo; no un mínimo matemático universal.')

add('El cálculo de área puede reconstruirse celda por celda','21 · Cuenta verificable','ledger',
    'El ejemplo usa el reporte real INT8/16 con Nangate45. Cada fila representa un tipo de celda con su multiplicidad y su área de biblioteca. Los restantes tipos combinacionales se agrupan solo para legibilidad de la diapositiva; el reporte CSV conserva cada tipo. Los96DFF_X1 aportan434.112unidades de área. Al sumar todas las instancias se obtiene7578.872, igual a stat-liberty. La unidad física se respalda con el databook original, que etiqueta um2; el estándar Liberty no impone una unidad universal para todos los paquetes.',
    refs=['F04','F11'],local='int8_16/nangate45/report.json · stat.json · cells.lib',
    takeaway='Contar instancias × área de celda es distinto de estimar área con LUT, tamaño de archivo o nodo.')

add('La clasificación distingue lógica, FF, latches y macros por semántica','22 · Contabilidad y rechazos','code',
    'El lector local elimina comentarios preservando cadenas y recorre los bloquescell. Exige area finita no negativa y nombres únicos. La categoría se obtiene por gruposff/ff_bank, latch/latch_bank y memory; no por reconocer letras en el nombre de una celda. El resumen cuenta tipos del módulo top aplanado, rechaza memorias sin mapear y tipos que no aparecen en Liberty. Los tres catálogos concretos han sido revisados; este parser acotado no se presenta como un parser universal de todo Liberty posible.',
    local='infrastructure/liberty.py · read_cells() / summarize_netlist()',
    code='counts = Counter(\n  cell["type"] for cell in module["cells"].values()\n)\nunknown = set(counts) - set(cells)\nif unknown: raise PipelineFailure(...)\n\nsubtotal = definition.area * count\ncategories[definition.category] += subtotal\n\n# Decimal durante la suma; float al serializar JSON',
    explanation='Se rechazan:\n\n• Tipos sin mapear.\n• Áreas inválidas o ausentes.\n• Diseño vacío.\n• Memorias pendientes.\n• Estado fuera del perfil.',
    takeaway='Una celda desconocida detiene el reporte; no se elimina para forzar un número.')

add('La netlist se contrasta con el RTL usando modelos del mismo Liberty','23 · Simulación posterior al mapeo','code',
    'Yosys importa funciones del Liberty sin-lib y genera cells_sim.v. Las opcionesignore_miss permiten omitir definiciones no soportadas del catálogo; si una celda utilizada falta o no elabora correctamente, Icarus o la comparación debe fallar. El mismo conjunto de vectores se usa contra mapped.v y se exige igualdad de cuatro estados mediante!==. Se comprueba además el marcador de256casos. Esta simulación es funcional sin SDF; los retrasos del testbench no caracterizan caminos de silicio.',
    refs=['F03','F07'],local='validation.py · validate_mapped() · simulation_cells.ys',
    code='yosys -s simulation_cells.ys\niverilog -g2012 -s area_validation_tb \\\n  -o mapped_sim validation_tb.v mapped.v cells_sim.v\nvvp mapped_sim\n\nif (r !== expected) $fatal(1, "Mapped mismatch...");',
    explanation='Referencia: rtl-results.txt.\n\nComparación: bit a bit.\n\nSe rechazan X/Z y diferencias.\n\nNo se cargan retardos SDF.',
    takeaway='256 coincidencias respaldan los casos ejercitados; no equivalencia exhaustiva ni precisión ideal.')

add('La confianza surge de controles complementarios, con límites distintos','24 · Sustentación del método','table',
    'No existe un único control que convierta todos los datos en verdad física. La identidad de bytes conecta una corrida con sus entradas. La cuenta por tipos conecta su área con el catálogo. La comparación con stat reduce errores del adaptador, pero ambas cuentas comparten la caracterización física de Liberty. La simulación limita regresiones en los casos recorridos. El oráculo entero añade independencia respecto al propio RTL. Formal, STA y PnR aportarían otros niveles, que este sistema no ha ejecutado.',
    refs=['F04','F05','F18'],local='auditar_evidencias.py · synthesis.py · validation.py',
    headers=['Control','Qué permite sostener','Qué no prueba'],
    rows=[['SHA-256','Mismos bytes de entrada','Corrección original o certificación externa'],['Suma ↔ stat','Coherencia contable','Otra caracterización física independiente'],['RTL ↔ netlist','Preservación en 256 estímulos','Todos los estados o entradas posibles'],['Oráculo INT','Producto punto modular en esos casos','Exactitud matemática de FP/Posit/LNS'],['Pruebas de software','Contratos, errores y filtros','Área física real de un chip']],
    widths=[2.05,4.4,4.8],
    takeaway='El argumento sólido declara exactamente qué riesgo cubre cada evidencia.')

add('El reporte conserva datos de cálculo y datos de procedencia','25 · Salidas y persistencia','cards',
    'La salida JSON integra áreas, conteos, tecnología, formato y validación junto al manifiesto. El CSV expone las filas por tipo de celda. SQLite conserva el estado y el reporte del experimento; la carpeta del run conserva fuentes, scripts y netlists. El ZIP de la aplicación reúne esos archivos y las fuentes anidadas, incluidas las unidades derivadasPosit. Los datos de validación histórica guardados en docs no se insertan automáticamente como trabajos ficticios en la base.',
    refs=['F16'],local='synthesis.py · api/routes.py · sqlite_repository.py',
    cards=[['report.json / CSV','Áreas por categoría, instancias y biblioteca. Estado de validación explícito.'],['manifest.json','Fuentes, Liberty, versiones, política y hashes de estímulos y respuestas.'],['ZIP + SQLite','El ZIP conserva artefactos; SQLite mantiene trabajos y resultados persistidos.']],
    takeaway='Una gráfica debe poder volver al UUID, manifiesto, script y reporte por celda.')

add('La comparación de la interfaz aplica filtros concretos','26 · Lectura correcta de los gráficos','cards',
    'ComparisonPanel ofrece dos modos. En tecnología filtra el design_id elegido y toma la última evaluación exitosa por technology_id. En formatos filtra una tecnología y toma la última exitosa por design_id. Se ordena por fecha, no por orden accidental de la lista. Actualmente no agrupa por hashes de script o biblioteca; para series futuras con versiones diferentes se debe comprobar la cohorte antes de comparar. La vista no simula datos ni precarga resultados. La lista de API devuelve los últimos100experimentos, lo que también limita el historial visible.',
    refs=['F14'],local='ComparisonPanel.tsx · contracts.ts · repository.list(limit=100)',
    cards=[['Entre tecnologías','La misma DPU; últimas corridas exitosas por biblioteca.'],['Entre formatos','Una biblioteca; última corrida exitosa de cada diseño.'],['Control que falta reforzar','Evitar mezclar versiones o políticas distintas solo porque coinciden los IDs.']],
    takeaway='Una comparación visual correcta requiere también una cohorte de entradas y políticas compatible.')

add('La evidencia completa alcanza 30 de las 33 combinaciones planeadas','27 · Cobertura real','coverage',
    'La matriz se construye leyendo qué report.json existen en el archivo, no asignando estados por conveniencia. Cada verde dispone de reportes, manifiesto, stat, vectores y dos marcadores de validación en un log. LNS16 no tiene esos tres reportes finales y se muestra como pendiente, sin área0ni valor interpolado. Son7680ejecuciones de vectores documentadas enRTL yotras7680enmapped; las tecnologías comparten conjuntos de estímulos por diseño y no deben venderse como7680muestras aleatorias independientes.',
    local='docs/validation/dpu-matrix-20261018/ · auditoria_evidencias.json',
    takeaway='30 casos documentados no significa que LNS16 ni las TCU completas estén validadas.')

add('El ejemplo INT8 muestra valores existentes y su fuente verificable','28 · Reporte real','chart',
    'El gráfico contiene exclusivamente los tres reportes almacenados de INT8/16. Las cifras se cargan del archivo auditado, no se escriben a mano como resultados. Todos incluyen96FF, el mismo RTL y la política indicada, pero catálogos, tensiones y tecnología son diferentes. La diferencia no permite concluir que la razón de áreas siga la leycuadrática del nodo ni que rindan igual. El valor es el área nominal total de celdas de la implementación mapeada.',
    refs=['F04'],local='int8_16/{ihp130,nangate45,nangate15}/report.json',
    chart='int8',takeaway='Es una comparación de bibliotecas e implementaciones; no de velocidad, potencia o silicio fabricado.')

add('Dentro de Nangate45, el formato cambia la implementación y el área','29 · Comparación con biblioteca fija','chart',
    'Esta gráfica usa los diez reportesNangate45completos. La tecnología queda fija para facilitar la lectura de diferencias entre implementaciones. Sin embargo los anchos, cantidad de registros, aritmética y redondeo no son iguales. No se afirma que la menor área represente mejor precisión o eficiencia de una aplicación. LNS16 se omite del gráfico de valores porque no tiene un reporte final; su ausencia se explicita en lugar de fabricar un resultado.',
    local='auditoria_evidencias.json · casos nangate45',
    chart='formats45',takeaway='LNS16 no se grafica: no existe un área final validada en el archivo.')

add('La auditoría volvió a comprobar el archivo sin ejecutar EDA','30 · Verificación de esta revisión','cards',
    'auditar_evidencias.py recorre únicamente artefactos guardados y los inputs actuales. Verifica hashes de originales y snapshots, identidad de manifiestos, perfiles, conteos de tipos contra stat, unidades derivadas Posit, hashes y vinculación de vectores. Recalcula las áreas con Decimal desde los tres Liberty y verifica salidas enteras. El máximo desacuerdo contable observado al recalcular es0bajo esta serialización. Las20pruebas backend y42frontend se ejecutaron hoy; las30integracionesEDA pertenecen al archivo anterior, no a nuevas corridas.',
    local='auditar_evidencias.py · auditoria_evidencias.json/.csv · pytest/vitest 19/10',
    cards=[['44 entradas','Originales y snapshots coinciden con los SHA-256 registrados.'],['30 cuentas de área','Filas y categorías coinciden con Liberty y stat. Desacuerdo observado: 0.'],['1.536 resultados INT','Recalculados en Python. Además: 20 tests backend y 42 tests frontend aprobados.']],
    takeaway='Hoy se verificó el archivo conservado; no se volvieron a sintetizar los circuitos.')

add('El archivo compacto permite auditar cuentas, pero no repetir toda la simulación','31 · Brecha de evidencia','cards',
    'Tras el episodio de presión de memoria se compactaron los temporales para liberar recursos. Se conservaron reportes, scripts, entradas de prueba, resultados y logs; no se conservaron mapped.v, mapped.json, design.v ni cells_sim.v de esas30corridas. Por ello hoy se cruza el desglose del reporte con stat y la biblioteca, pero no se vuelve a contar desde mapped.json ni se ejecuta la netlist. La aplicación sí está diseñada para incluir netlists en el ZIP al final de un run; para una publicación se debe retener ese paquete completo.',
    local='Inventario real de docs/validation/dpu-matrix-20261018/',
    cards=[['Conservado','Reportes, manifiestos, stat, scripts, vectores, testbenches y logs gzip.'],['No conservado','Netlists mapped.v / mapped.json, conversión design.v y modelos cells_sim.v.'],['Cierre recomendado','Retener el ZIP completo y sus hashes en futuras corridas controladas.']],
    takeaway='Los logs documentan una ejecución; no sustituyen los archivos necesarios para repetirla.')

add('LNS16 expuso un límite de recursos del entorno de pruebas','32 · Incidente y control operativo','cards',
    'LNS16 contiene tablas de corrección que aumentan la carga de conversión y optimización. Los ensayos locales coincidieron con presión de RAM y swap y fueron detenidos. El runner limita tiempo y mata el grupo al excederlo, pero no impone un límite de memoria al proceso local. Compose declara4GB,2CPUy128PIDs para el contenedor; esos límites no se aplicaban a los ensayos ejecutados directamente en la máquina. No se debe afirmar que aumentar timeout soluciona el problema ni que4GB bastan paraLNS. No se asignan resultados a sus tres casos pendientes.',
    local='process_runner.py · Settings · compose.yaml · lns16-incomplete/',
    cards=[['Límite temporal','900 s por comando; código de salida y stdout/stderr al log.'],['Límite de memoria','Compose: 4 GB y 2 CPU. El runner local no impone límite de RAM.'],['LNS16 pendiente','No cerrar sus tres casos hasta evaluar recursos en ejecución acotada.']],
    takeaway='Un fallo por recursos no invalida los otros reportes; tampoco habilita a inventar el faltante.')

add('La calidad del método depende de cerrar cuatro brechas concretas','33 · Mejoras antes de conclusiones fuertes','table',
    'La revisión encontró una base coherente y límites que conviene tratar como acciones, no como notas escondidas. Primero, retener artefactos completos y un digest de código, imagen y script por corrida; el manifiesto actual no guarda todo eso. Segundo, cerrar la cobertura pendiente deLNSsin volver a saturar la máquina. Tercero, separar preservación deRTLde exactitud matemática y desarrollar un oráculo independiente si se quiere hacer esa afirmación sobre otras familias. Cuarto, agrupar comparaciones por hashes y política además deID. Formal oSTAson trabajos adicionales solo si las preguntas de investigación requieren ese alcance.',
    local='Hallazgos de la auditoría de código y evidencias',
    headers=['Brecha','Por qué importa','Acción verificable'],
    rows=[['Artefactos / versiones','Repetir y revisar el resultado exacto','ZIP completo + hashes de código, imagen y script'],['LNS16 / recursos','Tres casos sin área publicada','Ejecutar con memoria y tiempo acotados'],['Oráculos no enteros','El RTL puede compartir un error con su referencia','Referencia numérica independiente si se afirma exactitud'],['Cohortes comparables','IDs iguales pueden ocultar cambios de biblioteca','Filtrar por hash y política de mapeo']],
    widths=[2.15,4.1,5.0],
    takeaway='Estas mejoras refuerzan las afirmaciones; no se presentan como implementadas hoy.')

add('La conclusión debe nombrar implementación, biblioteca y nivel de prueba','34 · Sustentación para la reunión','verdict',
    'Una formulación rigurosa es: para la DPU y wrapper concretos, con snapshots y condiciones identificados, este flujo produjo una implementación mapeada cuyo área nominal de celdas es la suma auditada de sus instancias. Se documentó preservación funcional para256estímulos y una referencia modular independiente en los perfiles enteros. No debe decirse que se demostró área final del chip, mínimo global, equivalencia exhaustiva, frecuencia objetivo ni precisión numérica independiente de todas las familias. El valor de la presentación es permitir a un revisor aceptar o refutar cada eslabón con evidencia.',
    refs=['F01','F04','F06','F18'],local='Código auditado + 30 paquetes de evidencia',
    statement='“Estimación prelayout del área nominal de celdas de la DPU registrada, mapeada con la biblioteca y política documentadas.”',
    left='Sustentado: identidad de entradas, cuenta de celdas y comportamiento en los casos registrados.',
    right='Pendiente: cobertura LNS16, archivo completo y cualquier afirmación de precisión, timing o silicio.',
    takeaway='Es defendible como estudio de área de celdas, con validación y límites expresamente acotados.')

add('La revisión necesita decisiones sobre evidencia y alcance','35 · Preguntas para feedback','cards',
    'Estas preguntas llevan a decisiones técnicas concretas. El grupo puede aprobar el alcance de celdas y wrappers, decidir si la caracterizaciónpredictiva es suficiente para el objetivo académico y definir el estándar de conservación de artefactos. También debe decidir si quiere comparar solo área o añadir precisión, potencia o frecuencia, lo que requeriría otros controles y experimentos. Las propuestas adicionales delExcel no se habilitan ni ejecutan por presentar esta diapositiva.',
    cards=[['Alcance','¿Se acepta área de celdas con wrapper, sin PnR ni objetivos de frecuencia?'],['Evidencia','¿Se exige ZIP completo, hashes de código/imagen y repetición controlada antes de publicar?'],['Ampliación','¿Se prioriza cerrar LNS16, estudiar otros corners o desarrollar oráculos numéricos?']],
    takeaway='El visto bueno debe referirse al método y a sus condiciones, no a una precisión física no demostrada.')

# Technical appendix: concrete detail stays editable and available for questions.
add('Anexo A · El mapa de archivos conecta cada afirmación con su implementación','Anexo técnico','table',
    'Las rutas son relativas a asic-area-lab. Conviene abrir estos archivos durante la reunión si se cuestiona cómo se obtiene una cifra. La presentación conserva la fecha y hashes del código revisado en auditoria_evidencias.json; esos hashes describen el estado de revisión, no prueban un digest de aplicación capturado cuando corrieron las síntesis anteriores.',
    local='backend/src/area_lab/ · frontend/src/',
    headers=['Responsabilidad','Archivo / símbolo'],
    rows=[['Perfil y tecnología','infrastructure/designs.py · catalog.py'],['Contrato de entrada','api/schemas.py · CreateExperimentRequest'],['Cola y estado','application/services.py · ExperimentService'],['Preparación VHDL','infrastructure/vhdl.py · analyze_sources'],['Oráculo y comparación','infrastructure/validation.py'],['Síntesis y reportes','infrastructure/synthesis.py · GhdlYosysSynthesis.run'],['Área y categorías','infrastructure/liberty.py'],['Ejecución externa','infrastructure/process_runner.py'],['Persistencia / descargas','infrastructure/sqlite_repository.py · api/routes.py'],['Filtros de gráficos','frontend/src/features/experiments/ComparisonPanel.tsx']],
    widths=[3.0,8.25],dense=True)

add('Anexo B · Los comandos de simulación RTL quedan registrados','Anexo técnico','code',
    'El testbench se analiza en work para instanciar el wrapper. La elaboración-eenlaza un ejecutable con el backendLLVM y requiere compiladorC,linker y zlib de desarrollo. La ejecución-rse detiene si falla una aserción. El desactivar asercionesIEEEaltiempo0solo suprime avisos de inicialización, no quita las aserciones del testbench en los resultados muestreados. La comprobación del número de salidas y de bits definidos ocurre también enPython.',
    refs=['F01'],local='validation.py · validate_rtl()',
    code='ghdl -a --std=08 -fsynopsys -fexplicit validation_tb.vhd\nghdl -e --std=08 -fsynopsys -fexplicit area_validation_tb\nghdl -r --std=08 -fsynopsys -fexplicit \\\n  area_validation_tb --assert-level=error \\\n  --ieee-asserts=disable-at-0\n\n# Exigir VALIDATION_OK 256 y 256 salidas definidas',
    explanation='-a: analizar.\n\n-e: elaborar y enlazar.\n\n-r: simular y fallar ante aserciones.\n\nEl log conserva comando, salida, exit code y duración.')

add('Anexo C · La memoria y los registros tienen una política explícita','Anexo técnico','cards',
    'Estos perfiles sonDPUcombinacionales con wrappersregistrados. LNSincluye tablasROMde corrección. La síntesis genérica reduce memorias a lógica y el resumen rechaza cualquier memoria residual del módulo top. No se mapea una macroSRAMni se modela una memoria comercial; un área de SRAM exigiría unlibertymacrocompatible, funcionalidad y política de mapeo documentadas. El código rechaza macros y latches inesperados para estos perfiles. Las constantes pueden eliminar registros cuyo valor sea no observable, por lo que los bits declarados no son siempre el conteo real deFF.',
    local='synthesis.py · memory_policy · summarize_netlist()',
    cards=[['Registros','Incluidos; FF reales según la netlist. INT8: 96, INT16: 192 esperados.'],['ROM de corrección','Se implementa como lógica combinacional, no como macro SRAM.'],['Control de salida','Se rechazan memorias residuales, latches y macros inesperadas.']])

add('Anexo D · Las API permiten seguir y auditar un experimento','Anexo técnico','table',
    'UUIDvalida el identificador y los artefactos se buscan enla carpeta de ese experimento, no en una ruta proporcionada por el cliente. El log porHTTPestá limitado a los últimos100KB; elZIPconserva el archivo completo. CSVrequiere estadoexitoso; ZIPrechazaqueuedorunning, pero puede devolver evidencia diagnóstica de unfallo. La cola llena devuelve429y los diseños/técnologías fuera del contrato son rechazados. El estado health=ok solo acreditarespuestaHTTP; no es untest de síntesis de unaDPU.',
    local='api/routes.py · main.py',
    headers=['Endpoint','Uso / condición'],
    rows=[['GET /api/v1/catalog','Perfiles y bibliotecas habilitadas'],['POST /api/v1/experiments','Crea UUID; devuelve 202'],['GET /api/v1/experiments/{id}','Estado y reporte del caso'],['GET /api/v1/experiments/{id}/logs','Cola del log; hasta 100 KB'],['GET /api/v1/experiments/{id}/artifacts','ZIP; disponible al terminar o fallar'],['GET /api/v1/experiments/{id}/report.csv','Desglose por celda; exige succeeded'],['GET /api/health','Salud HTTP, no validez de área']],
    widths=[6.6,4.65],dense=True)

areas=[]
for d in DESIGNS:
    vals=[]
    for t in ['ihp130','nangate45','nangate15']:
        r=reports.get((d.id,t)); vals.append(f"{r['total_area']:,.6f}" if r else 'PENDIENTE')
    areas.append([d.id,*vals])
add('Anexo E · Tabla trazable de áreas documentadas','Anexo técnico','table',
    'Las cifras se cargan de los reportes auditados. Se muestran seis decimales para conservar trazabilidad del valor serializado, no como una afirmación de exactitud física almicrómetrodecimal. Los resultados son prelayout, corners nominales propios y la política citada. Toda cifra de la tabla tiene un reporteJSON,unstaty unlog. La unidadµm²se usa según la convención de las bibliotecas; su evidencia bibliográfica se incluye en fuentes. LNSse mantiene como pendiente.',
    refs=['F04','F11'],local='auditoria_evidencias.csv · tabla generada desde report.json',
    headers=['DPU','IHP130 · µm²','Nangate45 · µm²','Nangate15 · µm²'],rows=areas,widths=[2.25,3,3,3],dense=True,
    takeaway='Los decimales expresan la cuenta de biblioteca, no la incertidumbre de un chip real.')

add('Anexo F · Release fijada no significa imagen completamente identificada','Anexo técnico','cards',
    'DockerfilefijaOSS_CADSuite2026-09-04y suSHA256.Esoayuda a repetir herramientas, pero el manifiesto aún no almacena digest final de imagen, hash integral del código y de cada script. Las imágenesbase están etiquetadas, no fijadas por digest en esteDockerfile. Los manifiestos guardanGHDL7.0.0-dev, Yosys0.68+182 eIcarus14.0devel; se deben preservar identificadorescompletos, no sustituirlos por estableactual. Las pruebas ligeras de hoy no actualizan retrospectivamente la procedencia de las síntesis anteriores.',
    refs=['F12','F17'],local='Dockerfile · manifest.tool_versions · auditoria_evidencias.json',
    cards=[['Suite fijada','OSS CAD Suite 2026-09-04 y SHA-256 del archivo descargado.'],['Versiones retenidas','GHDL 7.0.0-dev; Yosys 0.68+182; Icarus 14.0 devel.'],['Refuerzo recomendado','Digest de imagen, código y scripts por corrida; preservar los binarios o el contenedor.']])

add('Anexo G · La comprobación del build detecta fallos reales del toolchain','Anexo técnico','code',
    'El runtimeincluyebuild-essentialy zlib1g-devporqueGHDLLLVMnecesitaccy enlazar-lz.La imagenTrixieproporcionaglibcsuficiente para símbolos requeridos por la suitepinned; el comentario delDockerfile explica la dependencia.Elbuilds ejecutacheck_toolchain.pycomo usuario sinroot, analizando,elaborando,simulando yconvirtiendo un circuitopequeño.Ese smoketestpuede detectar instalaciónrotaqueversion--ocultaría.No sustituye simularcadaDPUni garantiza recursos suficientesparaLNS16.',
    local='Dockerfile · scripts/check_toolchain.py',
    code='RUN apt-get install ... build-essential zlib1g-dev\nUSER area-lab\nRUN python /app/scripts/check_toolchain.py\n\n# Verifica: compilador + enlace nativo\n# GHDL: análisis → elaboración → simulación → Verilog',
    explanation='Un smoke test de instalación.\n\nDetecta cc ausente y problemas de enlace.\n\nFalla el build si el toolchain está roto.\n\nNo ejecuta la matriz de DPU.')

add('Anexo H · Cómo repetir la auditoría sin sintetizar','Anexo técnico','code',
    'El comando mostrado relee archivos guardados, recalcula hashes y áreas y escribe un resumenJSON/CSV. No inicializa un servidorni abre cola de trabajos. Las pruebasnonintegrationusan gatewaysimulados o verifican funciones pequeñas; seexcluyen las integraciones que llamanEDA. Estas órdenes son una opción para revisar la cuenta sin repetir el trabajo de síntesis que saturó el equipo. Las pruebas frontendconstatancontratosyfiltrado,no circuitos.',
    local='auditar_evidencias.py · backend/tests · frontend/src/**/*.test.*',
    code='python3 docs/presentaciones/revision_pipeline_2026-10-19/\\\n  auditar_evidencias.py\n\n.venv/bin/pytest backend/tests -m "not integration" \\\n  -q -p no:cacheprovider\n\ncd frontend\nnpm test',
    explanation='Auditoría: 30 paquetes coherentes.\n\nPruebas ligeras: 20 backend.\n\nContratos e interfaz: 42 frontend.\n\nSin nuevas síntesis ni prueba de navegador.')

add('Anexo I · Referencias oficiales del procesamiento de hardware','Bibliografía','references',
    'Estas referencias describen capacidades y límites de las herramientas. Las versiones de documentación publicadas no seconfunden con las versiones exactas retenidas en cadamanifiesto. LasfichascompletasdeFUENTES_VERIFICADAS.mdincluyenautor,fechadeconsulta y advertencias de interpretación.',
    refs=['F01','F02','F03','F04','F05','F06','F07','F18'],ids=['F01','F02','F03','F04','F05','F06','F07','F18'])
add('Anexo J · Referencias de tecnología y plataforma','Bibliografía','references',
    'Las fuentes primarias de los PDK y bibliotecas separanprocesorealy modelopredictivo.Las referenciasdeplataformasrespaldan funcionesdeAPI,interfaz,empaquetadoypersistencia; noelárea deceldas.ElReadmelocalNangate15citaMartins2015y eldatabookNangate45indicaum2. Consultar eldocumentodefuentespararespaldo puntual de unidades y limitaciones.',
    refs=['F08','F09','F10','F11','F12','F13','F14','F15','F16','F17'],ids=['F08','F09','F10','F11','F12','F13','F14','F15','F16','F17'])

# Additional stack definitions distinguish hosting/validation from EDA.
extra=[]
for title,notes,refs,rows in [
    ('Anexo K · El backend coordina y persiste; las herramientas EDA calculan',
     'Python implementa los casos de uso, la ejecución de procesos y la cuenta de área. Uvicorn es el servidor ASGI que aloja FastAPI; no es un motor de síntesis. FastAPI y Pydantic validan las solicitudes y estructuran las respuestas. SQLite conserva trabajos y reportes dentro del proceso, con modo WAL y una conexión por operación. Docker empaqueta el entorno y Compose declara recursos y volumen. La validez del dato de área depende de los adaptadores EDA y del cálculo auditado, no de elegir un framework web concreto.',
     ['F19','F20','F21','F13','F16','F17'],
     [['Python','Orquestación y cálculo','services.py, synthesis.py, liberty.py'],
      ['Uvicorn / ASGI','Servidor HTTP del proceso','Docker CMD; un worker HTTP'],
      ['FastAPI + Pydantic','Rutas y validación de solicitudes','IDs enumerados; OpenAPI'],
      ['SQLite / WAL','Base embebida persistente','Estado y reportes por UUID'],
      ['Docker / Compose','Entorno y límites declarados','Imagen, volumen y recursos']]),
    ('Anexo L · El frontend valida contratos y representa reportes reales',
     'React construye la interfaz por componentes. TypeScript comprueba tipos durante desarrollo y construcción; no valida por sí solo JSON que llega por red. Zod comprueba los contratos de respuesta en ejecución antes de representarlos. TanStack Query gestiona consultas, estados y caché; el código refresca experimentos cada1500ms cuando hay trabajo activo, y cada5000ms en caso contrario. Vite compila archivos estáticos de producción que sirve FastAPI. Ninguna de estas piezas calcula área de puertas ni acredita corrección del circuito.',
     ['F14','F15','F22','F23','F24'],
     [['React','Componentes, propiedades y estado','Formulario, reporte y comparación'],
      ['TypeScript','Tipos estáticos del código','No sustituye validar JSON en runtime'],
      ['Zod','Validación de respuestas HTTP','schema.parse(data) antes de la UI'],
      ['TanStack Query','Consultas, caché y polling','1,5 s con trabajos; 5 s sin trabajos'],
      ['Vite','Desarrollo y build del frontend','No es otro servicio de producción']]),
]:
    extra.append(dict(title=title,section='Anexo técnico',type='table',notes=notes,refs=refs,
                      local='Dockerfile · main.py · api/schemas.py · hooks.ts · shared/api.ts',
                      headers=['Tecnología','Función','Uso concreto en el programa'],rows=rows,widths=[2.55,4.1,4.6]))
where=next(i for i,s in enumerate(slides) if s['type']=='references')
slides[where:where]=extra
slides.append(dict(title='Anexo M · Fuentes de lenguajes, servidor y validadores',
                   section='Bibliografía',type='references',
                   notes='Estas referencias oficiales respaldan las funciones de las tecnologías auxiliares. Se distingue validación de tipos y contratos de la validación funcional del hardware. Los archivos de dependencias del proyecto identifican las versiones instaladas; esta bibliografía describe las capacidades de cada proyecto, no demuestra una ejecución de síntesis.',
                   refs=['F19','F20','F21','F22','F23','F24'],ids=['F19','F20','F21','F22','F23','F24'],local=''))

# Bibliography gets its own readable pages rather than shrinking ten rows.
overview=dict(
    title='Una ejecución conecta entradas, referencia RTL, mapeo y reporte',
    section='11B · Pipeline completo',type='pipeline',refs=['F01','F02','F04','F07'],
    local='GhdlYosysSynthesis.run() · validation.py · liberty.py',
    notes='Este diagrama resume una ejecución real. Se elige perfil y Liberty, se copian y registran entradas, y GHDL simula el RTL para producir la referencia. Luego se convierte a Verilog, se sintetiza y mapea en Yosys, y se obtiene la netlist. Se comprueban conteos y áreas con Liberty y stat antes de simular la netlist contra la referencia RTL. Solo después se publica el reporte. La flecha de referencia es un flujo de datos adicional, no otra fase de síntesis. Cualquier fallo detiene la publicación de área válida. Las fuentes y dependencias son locales a un UUID; no se sustituye ningún resultado faltante por una estimación inventada.',
    takeaway='El reporte se publica tras comprobar estructura, cuenta y comportamiento en los estímulos seleccionados.')
position=next(i for i,s in enumerate(slides) if s['section'].startswith('12 ·'))
slides.insert(position,overview)

# Copy-edit technical speaker notes without changing any command or slide data.
import re
editorial={
    'Anexo A':'Las rutas son relativas a asic-area-lab. Estos archivos conectan las decisiones de selección, ejecución, validación y representación. Se pueden abrir durante la reunión para revisar una cifra concreta. Los hashes del código guardados en auditoria_evidencias.json identifican la versión inspeccionada hoy. No son un digest de aplicación capturado cuando se ejecutaron las síntesis anteriores.',
    'Anexo B':'El testbench se analiza en work e instancia el wrapper. La opción -e elabora y enlaza el ejecutable de simulación con el backend LLVM; por eso se requieren compilador C, linker y zlib de desarrollo. La ejecución -r falla ante aserciones. --ieee-asserts=disable-at-0 suprime avisos IEEE de inicialización; no desactiva los controles de las salidas muestreadas. Python comprueba además cantidad y definición de resultados.',
    'Anexo C':'Los perfiles miden DPU combinacionales con wrappers registrados. LNS16 incluye tablas ROM de corrección que se reducen a lógica. No se utiliza una macro SRAM ni una memoria comercial. El resumen rechaza memorias sin mapear, macros y latches inesperados. Si se decide estudiar macros, se necesitarán biblioteca, modelo funcional y política de mapeo específicos. Los bits de registros declarados no siempre equivalen a FF mapeados: una optimización puede eliminar estado no observable.',
    'Anexo D':'La API valida UUID y busca los artefactos en la carpeta de ese experimento. El log HTTP expone como máximo los últimos 100 KB; el ZIP conserva el log completo. El CSV exige estado succeeded. El ZIP rechaza trabajos queued o running, pero admite diagnósticos de trabajos fallidos. Una cola llena devuelve 429; solicitudes fuera del contrato se rechazan antes de ejecutar comandos. El estado health=ok acredita respuesta HTTP, no una prueba del circuito.',
    'Anexo E':'Las cifras se cargan de los reportes auditados. Se conservan seis decimales para identificar los valores serializados, no para afirmar esa exactitud física. Cada valor tiene reporte, stat y log. Los corners tienen condiciones nominales propias y la política de mapeo indicada. La convención de unidades de las bibliotecas se documenta en las fuentes. LNS16 permanece pendiente: no se usa cero ni una interpolación para llenar esa fila.',
    'Anexo F':'El Dockerfile fija OSS CAD Suite 2026-09-04 y el SHA-256 del archivo descargado. Esto ayuda a repetir las herramientas, pero no captura por sí solo el entorno completo. El manifiesto histórico aún no contiene digest final de imagen, hash integral del código y hash de cada script. Las imágenes base se referencian por etiqueta. Se deben preservar los identificadores completos de las versiones de desarrollo, sin sustituirlos por una versión estable actual.',
    'Anexo G':'El runtime incluye build-essential y zlib1g-dev porque GHDL LLVM necesita cc y el enlace -lz. Trixie proporciona la versión de glibc que necesita el runtime de la suite fijada. El build ejecuta check_toolchain.py como usuario sin root y comprueba análisis, elaboración, simulación y conversión de un circuito pequeño. Puede detectar una instalación rota aunque --version funcione. No sustituye simular cada DPU ni garantiza memoria suficiente para LNS16.',
    'Anexo H':'La auditoría lee únicamente artefactos guardados y recalcula hashes, asociaciones de vectores y áreas. No abre un servidor ni una cola de trabajos. Las pruebas nonintegration usan gateways simulados o funciones pequeñas; se excluyen las integraciones que invocan herramientas EDA. Las pruebas frontend verifican contratos y filtros de presentación. Hoy pasaron 20 pruebas backend y 42 frontend, además de la auditoría estática de los 30 paquetes completos.',
    'Anexo I':'Las fuentes describen capacidades y límites de las herramientas, no prueban que todas esas capacidades se hayan ejecutado. Los comandos concretos y sus versiones están en cada manifiesto y log. FUENTES_VERIFICADAS.md conserva autor, fecha de consulta, enlaces y límite de cada afirmación. No se atribuyen pruebas formales a la aplicación por tener herramientas que podrían realizarlas.',
    'Anexo J':'Las fuentes primarias distinguen proceso fabricado y kit predictivo. Las referencias de plataforma describen API, interfaz, empaquetado y persistencia; no calculan el área. El README suministrado de Nangate15 cita el artículo de Martins y el databook de Nangate45 etiqueta áreas en um2. El documento de fuentes explica el respaldo de unidades y los límites de correspondencia entre versiones.',
}
for slide in slides:
    for prefix,replacement in editorial.items():
        if slide['title'].startswith(prefix+' ·'):
            slide['notes']=replacement
    notes=slide['notes']
    for old,new in {
        'loopHTTP':'loop HTTP','ghdl--chop':'ghdl --chop','genera256':'genera 256',
        'semilla20261005':'semilla 20261005','producir256':'producir 256','módulo2^bitsR':'módulo 2^bits(R)',
        'alcance50MHz':'alcance 50 MHz','código0':'código 0','read_liberty-lib':'read_liberty -lib',
        'mediante-noabc':'mediante -noabc','check-assert':'check -assert','96DFF_X1':'96 DFF_X1',
        'aportan434.112':'aportan 434.112','obtiene7578.872':'obtiene 7578.872','stat-liberty':'stat -liberty',
        'bloquescell':'bloques cell','gruposff/ff_bank':'grupos ff/ff_bank','ignore_miss':'ignore_miss',
        'el modoWAL':'el modo WAL','son7680':'son 7680','yotras7680':'y otras 7680',
        'de256casos':'de 256 casos','FFen':'FF en','delRTL':'del RTL','referenciaRTL':'referencia RTL',
        'Las20':'Las 20','y42':'y 42','las30':'las 30','deLNSsin':'de LNS sin',
        'cuatro100':'cuatro 100','porHTTP':'por HTTP','reportesJSON':'reportes JSON',
        'retenerese':'retener ese','las30corridas':'las 30 corridas','catálogoPVT':'catálogo PVT',
        'controlesIEEE':'controles IEEE','capacidadRAM':'capacidad RAM',
    }.items(): notes=notes.replace(old,new)
    notes=re.sub(r'\b(al|de|Los|los|las|Las|con|en)(?=\d)',r'\1 ',notes)
    notes=re.sub(r'(?<=\d)(?=(?:casos|reportes|bits|estímulos|resultados|combinaciones|corridas|pruebas|archivos|unidades|backend|frontend|enteros|copias|FF|GB|CPU|PIDs))',' ',notes)
    notes=re.sub(r'(?<=[a-záéíóú])\.(?=[A-ZÁÉÍÓÚ])','. ',notes)
    notes=re.sub(r'(?<=[a-záéíóú])(?=(?:GHDL|Yosys|Icarus|Liberty|RTL|LNS16|INT8|INT16|Posit16|Posit32|SQLite|Docker|Python|Compose))',' ',notes)
    slide['notes']=notes

expanded=[]
for slide in slides:
    for before,after in [
        ('Anexo K · El backend','Anexo I · El backend'),
        ('Anexo L · El frontend','Anexo J · El frontend'),
        ('Anexo I · Referencias','Anexo K · Referencias'),
        ('Anexo J · Referencias','Anexo L · Referencias'),
    ]:
        if slide['title'].startswith(before):
            slide['title']=slide['title'].replace(before,after,1)
            break
    if slide['type']=='references':
        from math import ceil
        chunk_size=ceil(len(slide['ids'])/ceil(len(slide['ids'])/5))
        for start in range(0,len(slide['ids']),chunk_size):
            part=dict(slide)
            part['ids']=slide['ids'][start:start+chunk_size]
            part['title']=slide['title']+' · '+str(start//chunk_size+1)
            expanded.append(part)
    else:
        expanded.append(slide)
slides=expanded
(HERE/'contenido.json').write_text(json.dumps(dict(title='Revisión técnica del pipeline ASIC · GIRA',date='2026-10-19',slides=slides),indent=2,ensure_ascii=False)+'\n')
print(f'Prepared {len(slides)} slides from audited evidence.')
