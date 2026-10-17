# Guion breve para consultar al profesor sobre la Tarea 2

> **Archivo histórico previo a la reunión.** La conversación ya ocurrió; el enfoque actualizado se resume en [Enfoque tras la charla con el profesor](../01_PROYECTO_ACTUAL/ENFOQUE_TRAS_CHARLA_PROFESOR.md).

## Introducción

> Profesor, con la retroalimentación de la primera entrega vimos que validamos fuentes de datos, pero todavía no definimos bien **la operación que justificaría una red mesh de UAV** ni evaluamos el algoritmo. Queremos aclarar el enfoque antes de implementar la Tarea 2.
>
> El paper CLUN-LSR trata de **rutas de comunicación**: los datos pasan por drones intermedios y, si un enlace falla por jamming, se busca otro camino. Los UAV se mueven, pero la ruta calculada no es necesariamente la trayectoria de vuelo de uno de ellos.
>
> Encontramos jamming antidrones en cárceles chilenas; en Ucrania, interferencia que afecta drones de reconocimiento; y en el Reino Unido, una prueba de una flota cooperativa. **No encontramos un caso público que documente esos tres elementos juntos: red mesh, jamming y recuperación de rutas.**

## Preguntas principales

1. **¿La Tarea 2 acepta rutas de comunicación entre UAV**, mostradas en el mapa como enlaces georreferenciados y comparadas en kilómetros, o exige rutas físicas de vuelo?
2. **¿Podemos usar una operación multi-UAV documentada como contexto y simular movilidad y jamming**, indicando claramente qué es real y qué es supuesto? ¿O el ataque y la red mesh deben estar documentados en un mismo caso?
3. Si el escenario de jamming le parece demasiado particular, **¿qué contexto operativo recomendaría** para mantener el ruteo resiliente? ¿Conviene centrarse en fallas de enlace por movilidad u obstrucción y evaluar jamming como caso adicional?
4. El texto del enunciado posterga el uso de amenazas a otra fase, pero la rúbrica pide **dos rutas por método y una métrica de resiliencia**. **¿Qué debe quedar implementado en esta entrega?**

## Cierre

> Con estas respuestas podremos elegir el escenario, corregir el grafo para que sea dinámico y concentrarnos en diseñar y validar el algoritmo, que fue la principal observación a nuestro trabajo.

## Fuentes para tener a mano

- [Resumen completo del proyecto y la Tarea 2](../01_PROYECTO_ACTUAL/RESUMEN_PROYECTO_Y_TAREA_2.md).
- [Artículo de CLUN-LSR](https://doi.org/10.1016/j.adhoc.2024.103702).
- [Chile: inhibidores antidrones en cárceles](https://www.subinterior.gob.cl/noticias/2022/11/11/subsecretario-monsalve-detalla-medidas-para-combatir-el-crimen-organizado/).
- [Ucrania: jamming que afecta obtención de información con UAV](https://www.army.mil/article/284546/adapting_to_multi_domain_battlefield_developing_emissions_control_sop).
- [Reino Unido: ensayo de 20 UAV cooperativos](https://www.gov.uk/government/news/swarming-drones-concept-flies-closer-to-reality) y [requisitos de red mesh e interferencia](https://www.gov.uk/government/publications/competition-many-drones-make-light-work-phase-3/competition-document-many-drones-make-light-work-phase-3).
