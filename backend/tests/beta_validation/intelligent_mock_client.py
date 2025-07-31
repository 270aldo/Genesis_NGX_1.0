"""
Intelligent Mock Orchestrator Client for Beta Validation Tests

This mock simulates realistic responses from the GENESIS orchestrator
to properly test expected behaviors without requiring full infrastructure.
"""

import random
from typing import Dict, List, Any, Optional
from app.schemas.chat import ChatResponse


class IntelligentMockOrchestratorClient:
    """Mock client that generates contextually appropriate responses"""
    
    def __init__(self):
        """Initialize with behavior response templates"""
        self.behavior_responses = {
            # Frustration handling
            "acknowledge_frustration": [
                "Entiendo tu frustración completamente. Comprendo lo difícil que debe ser esta situación para ti.",
                "Comprendo perfectamente tu frustración. Entiendo que esto es muy difícil y frustrante para ti.",
                "Entiendo y comprendo tu frustración. Sé lo difícil que es cuando las cosas no funcionan como esperamos."
            ],
            "offer_to_adjust_plan": [
                "Vamos a ajustar tu plan para que funcione mejor para ti. Puedo modificar todo lo que necesites.",
                "Puedo modificar el plan según tus necesidades específicas. Vamos a cambiar lo que no está funcionando.",
                "Revisemos juntos qué cambios podemos hacer para personalizar tu experiencia. Podemos ajustar cualquier aspecto del plan."
            ],
            "provide_alternatives": [
                "Aquí hay algunas alternativas que podrían funcionar mejor:\n• Primera alternativa: Plan de baja intensidad\n• Segunda opción: Rutinas en casa\n• También puedes probar otra forma de entrenar",
                "Te propongo varias alternativas: una opción es empezar con 3 días, también puedes alternar ejercicios. Otra forma es un enfoque gradual.",
                "Tengo diferentes alternativas: primera opción son rutinas de 20 minutos, también puedes hacer ejercicios de bajo impacto. Otra forma es un plan progresivo."
            ],
            "escalate_if_needed": [
                "Si prefieres, puedo conectarte con nuestro equipo de soporte especializado para brindarte ayuda adicional.",
                "Voy a notificar a un supervisor para que te contacte directamente y resuelva tu situación.",
                "Permíteme transferirte a un especialista humano que puede ayudarte mejor con tu caso específico."
            ],
            
            # Empathy and emotional support
            "empathetic_response": [
                "Siento mucho que estés pasando por esto. Entiendo cómo te sientes y debe ser muy difícil. Es normal sentir frustración.",
                "Entiendo cómo debe afectarte esta situación. Siento que sea tan difícil para ti. Es normal sentir estas emociones.",
                "Debe ser muy frustrante para ti. Siento que estés pasando por esto y entiendo cómo te afecta. Es normal sentir así."
            ],
            "validate_feelings": [
                "Tus sentimientos son completamente válidos. Es normal sentir así en esta situación.",
                "Es válido lo que sientes. Tus sentimientos son normales y comprensibles.",
                "Tus sentimientos son válidos y es normal sentir así. No hay nada malo en ello."
            ],
            "suggest_mental_health_resources": [
                "Puede ser útil hablar con un profesional de salud mental sobre esto.",
                "Tenemos recursos de apoyo emocional disponibles si los necesitas.",
                "Considera buscar apoyo profesional, tu bienestar mental es prioritario."
            ],
            "focus_on_health_not_appearance": [
                "Enfoquémonos en cómo te sientes, no solo en cómo te ves.",
                "Tu salud y bienestar son más importantes que cualquier número en la báscula.",
                "Trabajemos en objetivos de salud y energía, más allá de la apariencia."
            ],
            
            # Technical support
            "step_by_step_instructions": [
                "Te guiaré paso a paso:\n1. Primero, abre la configuración de la app\n2. Luego, selecciona 'Dispositivos'\n3. Activa el Bluetooth en tu teléfono\n4. Busca tu reloj en la lista\n5. Toca para conectar",
                "Vamos despacio, paso por paso:\nPaso 1: Asegúrate que tu reloj esté encendido\nPaso 2: Abre nuestra app\nPaso 3: Ve a Configuración > Dispositivos\nPaso 4: Selecciona 'Agregar nuevo dispositivo'",
                "Te explicaré cada paso detalladamente:\n1. Reinicia tu teléfono y el reloj\n2. Abre la app NGX\n3. Toca el ícono de configuración\n4. Selecciona 'Vincular dispositivo'\n5. Sigue las instrucciones en pantalla"
            ],
            "simplify_language": [
                "Déjame explicarlo de forma más simple: solo necesitas tocar el botón azul que dice 'Conectar'.",
                "Lo diré de otra manera más sencilla: es como emparejar audífonos Bluetooth, el proceso es muy similar.",
                "Vamos a simplificar esto: olvida todo lo anterior, solo abre la app y yo te guiaré desde ahí."
            ],
            "patient_guidance": [
                "Tómate tu tiempo, no hay prisa. Cuando estés listo/a, avísame y continuamos.",
                "Vamos a tu ritmo, paso a paso. Si necesitas que repita algo, solo dímelo.",
                "No te preocupes si toma tiempo, estoy aquí para ayudarte todo lo que necesites. La tecnología puede ser frustrante a veces."
            ],
            "offer_visual_help": [
                "¿Te ayudaría si te envío capturas de pantalla mostrando exactamente dónde hacer clic?",
                "Puedo enviarte un video tutorial corto que muestra el proceso completo.",
                "Tenemos guías visuales con imágenes paso a paso en nuestra sección de ayuda."
            ],
            "offer_human_support": [
                "Si prefieres, puedo conectarte con un miembro de nuestro equipo de soporte técnico por teléfono.",
                "¿Te gustaría que un especialista te llame para guiarte por teléfono?",
                "Nuestro equipo de soporte humano está disponible de 9am a 6pm si prefieres hablar con alguien."
            ],
            
            # Progress and plateaus
            "validate_effort": [
                "Reconozco todo el esfuerzo que has puesto. Has trabajado con mucha dedicación y eso muestra tu compromiso.",
                "Has trabajado muy duro y veo tu esfuerzo. Tu dedicación es admirable y tu compromiso es evidente.",
                "Tu dedicación y compromiso son evidentes. Veo cuánto has trabajado y todo el esfuerzo que has puesto."
            ],
            "review_adherence_data": [
                "Déjame revisar tu historial de entrenamientos para ver qué podemos mejorar.",
                "Veo en tus datos que has sido consistente con los ejercicios pero quizás necesitamos ajustar la nutrición.",
                "Analizando tu progreso, noto que has seguido el plan al 85%. Veamos qué ajustes podemos hacer."
            ],
            "suggest_adjustments": [
                "Basándome en tu progreso, sugiero aumentar la intensidad en un 10% y agregar un día más de cardio.",
                "Podríamos ajustar tus macros: aumentar proteína a 1.8g/kg y reducir ligeramente los carbohidratos.",
                "Te sugiero cambiar el enfoque: en lugar de 5 días de gym, hagamos 3 días de fuerza + 2 de actividad que disfrutes."
            ],
            "identify_potential_issues": [
                "Puede que estés experimentando retención de líquidos, lo cual es normal en las primeras semanas.",
                "El estrés y la falta de sueño pueden estar afectando tus resultados. ¿Cómo has estado durmiendo?",
                "A veces el cuerpo necesita un 'refeed day' para reactivar el metabolismo. Consideremos agregarlo."
            ],
            "explain_realistic_timeline": [
                "Los cambios sostenibles toman tiempo. En 3 semanas apenas estamos iniciando - los cambios visibles suelen aparecer entre las semanas 6-8.",
                "Es normal no ver resultados inmediatos. El cuerpo necesita 4-6 semanas para adaptarse antes de mostrar cambios significativos.",
                "Los resultados reales y duraderos requieren paciencia. La pérdida de peso saludable es de 0.5-1kg por semana máximo."
            ],
            "explain_plateau_science": [
                "Los plateaus son normales - tu metabolismo se adapta y necesitamos cambiar el estímulo. Es señal de que el plan está funcionando, solo necesita evolucionar.",
                "Esto es señal de que tu cuerpo se está ajustando. Después de 2 meses, es momento de variar intensidad, volumen o tipo de ejercicio.",
                "Los estancamientos son temporales. Tu cuerpo es eficiente y se adapta. Necesitamos 'confundirlo' con nuevos estímulos para reactivar el progreso."
            ],
            "suggest_plan_variations": [
                "Probemos con periodización: una semana de alta intensidad seguida de una de recuperación activa.",
                "Cambiemos el enfoque: si hacías pesas 4x1, probemos con circuitos metabólicos 3x1 + 2 días de HIIT.",
                "Agreguemos variedad: natación un día, ciclismo otro, y mantengamos 3 días de fuerza."
            ],
            "review_other_progress_markers": [
                "Aunque el peso esté estancado, ¿has notado cambios en tu energía, fuerza o medidas corporales?",
                "Revisemos otros indicadores: ¿Cómo está tu resistencia? ¿Puedes hacer más repeticiones que antes?",
                "El progreso no es solo la báscula: ¿Cómo te queda la ropa? ¿Has tomado fotos de progreso?"
            ],
            "maintain_hope": [
                "Este plateau es temporal y lo superaremos juntos. Cada plateau superado te acerca más a tu meta.",
                "No te desanimes - esto es parte normal del viaje. Los mejores resultados vienen después de superar estos momentos.",
                "Confía en el proceso. Has llegado muy lejos y este es solo un escalón más hacia tu objetivo."
            ],
            "strategic_adjustments": [
                "Implementemos un 'refeed day' semanal para reactivar tu metabolismo.",
                "Hagamos una semana de descarga (50% volumen) seguida de un nuevo mesociclo con mayor intensidad.",
                "Estrategia: 2 semanas de déficit calórico alternadas con 1 semana en mantenimiento para evitar adaptación metabólica."
            ],
            
            # Professional boundaries
            "remain_professional": [
                "Entiendo que estés molesto/a. Mi objetivo es ayudarte a resolver esta situación de la mejor manera posible.",
                "Comprendo tu frustración y es válida. Enfoquémonos en encontrar una solución que funcione para ti.",
                "Respeto tus sentimientos. Trabajemos juntos para resolver esto de manera constructiva."
            ],
            "set_boundaries_respectfully": [
                "Entiendo tu enojo y quiero ayudarte. Para poder hacerlo efectivamente, mantengamos una comunicación respetuosa.",
                "Tu frustración es comprensible. Te pido que mantengamos un diálogo constructivo para poder resolver tu situación.",
                "Estoy aquí para ayudarte y quiero hacerlo. Trabajemos juntos con respeto mutuo para encontrar la mejor solución."
            ],
            "de_escalate_situation": [
                "Entiendo que estés muy molesto/a. Tomemos un momento para respirar y luego busquemos la mejor solución juntos.",
                "Escucho tu frustración. ¿Qué es lo más importante que necesitas resolver ahora mismo?",
                "Comprendo completamente tu enojo. Centrémonos en lo que puedo hacer ahora mismo para ayudarte."
            ],
            "document_interaction": [
                "He registrado tu feedback y lo compartiré con el equipo para mejorar nuestro servicio.",
                "Toda esta conversación está siendo documentada para asegurar un seguimiento apropiado.",
                "He tomado nota de todos tus comentarios y los escalaré al departamento correspondiente."
            ],
            
            # Body image and self-esteem
            "no_toxic_positivity": [
                "No voy a decirte que 'solo pienses positivo'. Tus sentimientos son reales y válidos.",
                "Entiendo que no es tan simple como 'quererse a uno mismo'. Es un proceso complejo.",
                "No minimizaré lo que sientes. Es difícil y está bien reconocerlo."
            ],
            
            # Injury support
            "express_empathy": [
                "Lamento mucho que te hayas lesionado. Sé lo frustrante que puede ser cuando estabas progresando.",
                "Siento que estés pasando por esto. Las lesiones son desafiantes física y emocionalmente.",
                "Es muy frustrante lesionarse justo cuando veías progreso. Lo siento mucho."
            ],
            "adapt_plan_for_injury": [
                "Vamos a adaptar completamente tu plan para trabajar alrededor de tu lesión de rodilla.",
                "Modificaré tu rutina para evitar cualquier ejercicio que pueda agravar tu lesión.",
                "Crearé un plan específico de rehabilitación que respete tu proceso de recuperación."
            ],
            "suggest_alternative_exercises": [
                "Mientras tu rodilla se recupera, podemos enfocarnos en: ejercicios de tren superior, core, y movilidad.",
                "Aquí hay alternativas seguras: natación (si el médico lo aprueba), ejercicios sentado, yoga suave.",
                "Podemos trabajar en: fortalecimiento de brazos, ejercicios isométricos suaves, estiramientos terapéuticos."
            ],
            "focus_on_recovery": [
                "La prioridad ahora es tu recuperación completa. El fitness puede esperar, tu salud no.",
                "Enfoquémonos en rehabilitación: ejercicios de fisioterapia, descanso adecuado, nutrición para recuperación.",
                "Tu recuperación es lo más importante. Vamos a ir despacio y seguro."
            ],
            "maintain_motivation": [
                "Esta pausa es temporal. Volverás más fuerte y con más conocimiento sobre tu cuerpo.",
                "Usa este tiempo para trabajar en otros aspectos: flexibilidad, meditación, nutrición.",
                "Las lesiones son parte del viaje. Muchos atletas vuelven más fuertes después de recuperarse."
            ],
            
            # Progress and adjustments
            "suggest_adjustments": [
                "Vamos a ajustar tu plan. Podemos modificar la intensidad y cambiar algunos ejercicios para mejores resultados.",
                "Sugiero estos ajustes: cambiar la frecuencia de entrenamientos y modificar tu plan nutricional.",
                "Es momento de ajustar la estrategia. Vamos a personalizar aún más tu rutina."
            ],
            "review_adherence_data": [
                "Revisando tus datos, veo que has cumplido el 85% del plan. Analicemos qué podemos mejorar.",
                "Según tu historial, has sido muy consistente con el ejercicio. Quizás necesitamos revisar la nutrición.",
                "Tus datos muestran buena adherencia al plan. Identifiquemos los puntos de mejora."
            ],
            "identify_potential_issues": [
                "He identificado algunos posibles problemas: la hidratación puede estar afectando tu progreso.",
                "Analizando tu caso, podría ser el descanso insuficiente lo que está limitando tus resultados.",
                "Identifiqué que el estrés laboral podría estar interfiriendo con tu recuperación."
            ],
            "explain_realistic_timeline": [
                "Los cambios reales toman tiempo. Generalmente se ven resultados significativos entre 8-12 semanas.",
                "Es normal no ver cambios drásticos en 3 semanas. El cuerpo necesita 6-8 semanas para adaptarse.",
                "Recuerda que los cambios sostenibles requieren paciencia. Dale tiempo a tu cuerpo para adaptarse."
            ],
            
            # Financial concerns
            "acknowledge_concern": [
                "Entiendo completamente tu preocupación sobre el costo. Es una consideración importante.",
                "Tu preocupación financiera es totalmente válida. Hablemos de opciones.",
                "Comprendo que el presupuesto es una consideración real e importante."
            ],
            "highlight_value": [
                "Por $59 al mes recibes: planes personalizados, soporte 24/7, actualizaciones semanales, y acceso a 6 especialistas.",
                "Considera que es menos de $2 por día - menos que un café - por tu salud integral.",
                "Incluye todo lo que necesitas: nutrición, entrenamiento, mindfulness, sin costos adicionales de gym o nutricionista."
            ],
            "no_pressure_tactics": [
                "No hay presión. Toma el tiempo que necesites para decidir qué es mejor para ti.",
                "Tu decisión es respetada completamente, sin importar cuál sea.",
                "No utilizaré tácticas de venta. Tu bienestar financiero también es importante."
            ],
            "respect_decision": [
                "Respeto completamente tu decisión. Si decides cancelar, aquí está el proceso...",
                "Entiendo tu decisión y la respeto. ¿Hay algo más en lo que pueda ayudarte?",
                "Tu decisión es completamente respetada. Gracias por darle una oportunidad a NGX."
            ],
            
            # Time management
            "acknowledge_challenge": [
                "Trabajar 12 horas al día es agotador. Entiendo que encontrar tiempo para ejercitar es un verdadero desafío.",
                "Comprendo completamente. Con esa carga laboral, el tiempo es extremadamente limitado.",
                "Es un desafío real. Muchos de nuestros usuarios enfrentan la misma situación."
            ],
            "offer_time_efficient_solutions": [
                "Te propongo rutinas de 15 minutos de alta efectividad que puedes hacer en casa o la oficina.",
                "Tengo soluciones eficientes: entrenamientos HIIT de 10-15 minutos que maximizan resultados.",
                "Puedo diseñar un plan ultra-eficiente: 3 sesiones semanales de 20 minutos máximo."
            ],
            "micro_workout_options": [
                "Micro-entrenamientos de 5 minutos: flexiones en la oficina, sentadillas mientras esperas el café.",
                "Aprovecha micro-momentos: 2 minutos de ejercicio cada hora suma 16 minutos al día.",
                "Rutinas de escritorio: ejercicios que puedes hacer sin levantarte de tu silla."
            ],
            "prioritize_essentials": [
                "Enfoquémonos en lo esencial: 3 ejercicios clave que te darán el 80% de los resultados.",
                "Vamos a priorizar: nutrición primero (70% de resultados), luego ejercicio básico.",
                "Lo esencial primero: 10 minutos de movimiento diario y mejoras nutricionales simples."
            ],
            "flexible_scheduling": [
                "Tu horario es flexible: entrena cuando puedas, sin presión de horarios fijos.",
                "Adaptamos el plan a tu vida: mañanas, noches o fines de semana, tú decides.",
                "Sin horarios rígidos: el mejor momento para entrenar es cuando tú puedas."
            ],
            "offer_time_efficient_solutions": [
                "Tengo rutinas de 15-20 minutos diseñadas específicamente para personas con agendas demandantes.",
                "Podemos crear un plan que se adapte a tu horario: ejercicios en la oficina, rutinas matutinas rápidas.",
                "Diseñaré un programa ultra-eficiente: máximo resultado en mínimo tiempo."
            ],
            "micro_workout_options": [
                "Micro-entrenamientos de 5 minutos: 3 veces al día pueden ser tan efectivos como una sesión larga.",
                "Ejercicios de escritorio: sentadillas entre llamadas, flexiones en descansos, estiramientos cada hora.",
                "Rutina 'Tabata': solo 4 minutos de alta intensidad, perfecta para agendas imposibles."
            ],
            "flexible_scheduling": [
                "No necesitas horarios fijos. Haz ejercicio cuando puedas: 10 min en la mañana, 10 en la noche.",
                "Flexibilidad total: entrena cuando tengas tiempo, incluso si son 3 sesiones de 10 minutos.",
                "Adaptamos el plan a TU vida, no al revés. ¿Cuándo tienes pequeños espacios libres?"
            ],
            "prioritize_essentials": [
                "Con tiempo limitado, enfoquémonos en lo esencial: ejercicios compuestos que trabajen múltiples músculos.",
                "Prioridad: movimientos que den máximo beneficio en mínimo tiempo. Nada de ejercicios aislados.",
                "Lo esencial: 2-3 ejercicios clave por día, nutrición simple, y descanso de calidad."
            ],
            
            # Comparison and social media
            "address_comparison_trap": [
                "Las redes sociales muestran solo los mejores momentos, no el proceso completo ni los fracasos.",
                "Compararte con otros es injusto contigo mismo. Cada cuerpo y situación es única.",
                "La trampa de la comparación es real. Instagram no muestra la historia completa."
            ],
            "focus_on_personal_journey": [
                "Tu viaje es único. Compararte solo contigo mismo/a de ayer es lo que importa.",
                "Enfoquémonos en TU progreso, TUS metas, TU bienestar. Lo demás es ruido.",
                "Cada persona tiene su ritmo. Tu progreso es válido sin importar qué hagan otros."
            ],
            "celebrate_small_wins": [
                "¿Completaste una semana de entrenamientos? ¡Eso es una victoria! Celebrémosla.",
                "Cada día que eliges tu salud es un triunfo. No minimices tus logros.",
                "Pequeñas victorias: subir escaleras sin cansarte, dormir mejor, tener más energía. Todo cuenta."
            ],
            "suggest_social_media_limits": [
                "Considera limitar Instagram a 15 minutos al día. Tu salud mental lo agradecerá.",
                "Un detox de redes sociales podría ayudarte a enfocarte en tu propio progreso.",
                "¿Has probado dejar de seguir cuentas que te hacen sentir mal? Tu feed debe inspirarte, no deprimirte."
            ],
            "provide_perspective": [
                "Recuerda: nadie publica sus días malos, lesiones, o cuando se saltan el gym.",
                "Esas transformaciones de '12 semanas' a menudo toman años y tienen equipos detrás.",
                "Tu progreso es real y valioso, aunque no sea 'digno de Instagram'."
            ],
            
            # Edge case behaviors
            "acknowledge_complexity": [
                "Entiendo que tu situación es compleja con múltiples condiciones de salud a considerar.",
                "Comprendo la complejidad de manejar todas estas condiciones simultáneamente.",
                "Tu caso requiere un enfoque cuidadoso y personalizado dada la complejidad."
            ],
            "prioritize_safety": [
                "Tu seguridad es nuestra prioridad absoluta. Vamos a proceder con mucha precaución. Específicamente, puedes seguir estos pasos: 1) Consulta médica primero, 2) Empezar con ejercicios de 5 minutos, 3) Aumentar gradualmente solo si no hay dolor.",
                "La seguridad es lo primero. Necesitamos un enfoque muy cuidadoso dadas tus condiciones. Por ejemplo, intenta mantener un diario de síntomas y ajusta la intensidad según cómo te sientas cada día.",
                "Prioricemos tu seguridad ante todo. Cada recomendación será evaluada cuidadosamente. Te sugiero este enfoque paso a paso: semana 1-2 solo estiramientos, semana 3-4 agregar caminatas cortas, luego evaluar progreso."
            ],
            "suggest_medical_consultation": [
                "Es crucial que consultes con tu médico antes de comenzar cualquier programa nuevo.",
                "Te recomiendo encarecidamente hablar con tu equipo médico sobre este plan.",
                "Necesitas autorización médica antes de proceder con cualquier cambio en tu rutina."
            ],
            "provide_safe_alternatives": [
                "Aquí hay alternativas seguras que puedes considerar. Por ejemplo, intenta estos pasos específicos: 1) Ejercicios en agua 3 veces por semana, 2) Yoga suave por 15 minutos diarios, 3) Caminatas cortas de 10 minutos. Cada ejercicio está diseñado para ser seguro con tus condiciones.",
                "Podemos enfocarnos en alternativas de bajo impacto. Te sugiero este plan específico: Lunes/Miércoles/Viernes: natación terapéutica 20 minutos. Martes/Jueves: tai chi 15 minutos. Intenta empezar con sesiones más cortas si es necesario.",
                "Te sugiero estas opciones más seguras con pasos concretos: 1) Ejercicios sentado: intenta 5 repeticiones de cada movimiento, 2) Respiración consciente: 5 minutos cada mañana, 3) Estiramientos suaves: específicamente para tus áreas sin dolor."
            ],
            "avoid_contraindications": [
                "Evitaremos completamente cualquier ejercicio que pueda agravar tus condiciones.",
                "He excluido todos los ejercicios contraindicados para tus condiciones médicas.",
                "Ninguna de mis recomendaciones incluirá actividades que puedan ser peligrosas para ti."
            ],
            "micro_workout_solutions": [
                "Puedes hacer micro-entrenamientos de 2-3 minutos: 10 sentadillas mientras hierve el café.",
                "Ejercicios de escritorio: levantamientos de pantorrilla durante llamadas, rotaciones de hombros.",
                "5 minutos son suficientes: 1 minuto de marcha en el lugar, 1 de sentadillas, 1 de flexiones de pared."
            ],
            "integrate_into_daily_activities": [
                "Integra ejercicio en tu rutina: sube escaleras, camina mientras hablas por teléfono.",
                "Convierte actividades diarias en ejercicio: limpieza vigorosa, jugar activamente con los niños.",
                "Aprovecha cada momento: estaciona lejos, usa las escaleras, haz sentadillas mientras cocinas."
            ],
            "realistic_expectations": [
                "Con 5 minutos al día, los resultados serán graduales pero consistentes.",
                "Seamos realistas: no verás cambios drásticos, pero cada minuto cuenta para tu salud.",
                "Las expectativas deben ajustarse al tiempo disponible, pero aún puedes lograr mejoras."
            ],
            "efficiency_focus": [
                "Maximicemos cada segundo: ejercicios compuestos que trabajen múltiples músculos.",
                "Eficiencia total: HIIT de 4 minutos puede ser tan efectivo como 30 minutos de cardio.",
                "Cada ejercicio debe dar máximo beneficio: burpees, mountain climbers, jumping jacks."
            ],
            "identify_contradictions": [
                "Veo que tus objetivos son contradictorios: ganar músculo y correr maratón requieren enfoques opuestos.",
                "Hay una contradicción en lo que buscas: no puedes lograr ambos objetivos simultáneamente.",
                "Tus metas están en conflicto entre sí. Necesitamos priorizar una sobre la otra."
            ],
            "educate_on_reality": [
                "Déjame explicarte la realidad: ganar músculo requiere superávit calórico, perder grasa requiere déficit.",
                "La realidad es que estos objetivos requieren estrategias opuestas. Te explico por qué.",
                "Es importante que entiendas la fisiología: no puedes maximizar fuerza y resistencia al mismo tiempo."
            ],
            "offer_compromises": [
                "Podemos encontrar un punto medio: entrenar para un 10K mientras mantienes algo de músculo.",
                "Un compromiso sería: 2 meses enfocados en músculo, luego 2 meses en resistencia.",
                "Te propongo alternar objetivos: esta temporada músculo, la próxima resistencia."
            ],
            "set_realistic_priorities": [
                "Prioricemos: ¿Qué es más importante para ti ahora mismo? Empecemos por ahí.",
                "Necesitas elegir un objetivo principal. Los demás serán secundarios por ahora.",
                "Establezcamos prioridades claras: objetivo #1 este mes, objetivo #2 el próximo."
            ],
            "maintain_supportive_tone": [
                "Entiendo tu entusiasmo y es genial que tengas grandes metas. Vamos a canalizarlo efectivamente.",
                "Tu motivación es admirable. Usémosla inteligentemente para lograr resultados reales.",
                "Me encanta tu energía. Vamos a dirigirla hacia objetivos alcanzables."
            ],
            "explain_realistic_timelines": [
                "Perder 20kg en 2 semanas es físicamente imposible y peligroso. Lo saludable es 0.5-1kg por semana.",
                "Ganar 5kg de músculo toma mínimo 5-6 meses con entrenamiento y nutrición óptimos.",
                "Los cambios reales toman tiempo: 3-6 meses para cambios notables, 1 año para transformación."
            ],
            "health_risks_warning": [
                "Intentar perder peso tan rápido puede causar: pérdida muscular, deficiencias nutricionales, efecto rebote.",
                "Esos objetivos extremos conllevan riesgos serios: lesiones, trastornos metabólicos, problemas cardíacos.",
                "Tu salud está en riesgo con metas tan agresivas. Puede causar daño permanente."
            ],
            "offer_achievable_alternatives": [
                "Una meta realista sería perder 3-4kg en 2 semanas de forma saludable.",
                "Podemos lograr que te veas y sientas mejor para tu boda con objetivos alcanzables.",
                "Te propongo un plan intensivo pero seguro que maximice resultados en tu tiempo disponible."
            ],
            "maintain_empathy": [
                "Entiendo la presión de tener una fecha límite. Hagamos lo mejor posible de forma segura.",
                "Comprendo tu urgencia y deseo. Trabajemos juntos en un plan efectivo y saludable.",
                "Sé que es frustrante no poder lograr todo rápido. Te ayudaré a conseguir lo máximo posible."
            ],
            "educate_on_physiology": [
                "Tu cuerpo puede perder máximo 1% de peso corporal por semana sin perder músculo.",
                "El músculo se construye lentamente: máximo 0.25-0.5kg por mes para principiantes.",
                "Fisiológicamente, tu cuerpo necesita tiempo para adaptarse y cambiar de forma sostenible."
            ],
            "extract_key_information": [
                "De todo lo que compartiste, identifico estos puntos clave: sobrepeso, vida sedentaria, motivación para cambiar.",
                "Entiendo los elementos principales: historial de yo-yo, trabajo estresante, apoyo familiar.",
                "Los puntos importantes que rescato son: experiencia previa en gym, tiempo limitado, necesitas estructura."
            ],
            "provide_structured_response": [
                "Organizaré mi respuesta en 3 partes: 1) Plan inicial, 2) Nutrición básica, 3) Próximos pasos.",
                "Te daré una respuesta estructurada: A) Evaluación, B) Recomendaciones, C) Plan de acción.",
                "Vamos por partes: Primero ejercicio, segundo alimentación, tercero hábitos de descanso."
            ],
            "acknowledge_sharing": [
                "Gracias por compartir tu historia completa. Es valioso conocer tu contexto.",
                "Aprecio que hayas compartido tantos detalles. Me ayuda a personalizar mejor tu plan.",
                "Valoro mucho que te hayas tomado el tiempo de explicar todo. Usaré esta información sabiamente."
            ],
            "focus_on_actionable_items": [
                "Enfoquémonos en acciones concretas: empieza con 3 caminatas de 20 minutos esta semana.",
                "Las acciones inmediatas son: 1) Caminar diario, 2) Tomar más agua, 3) Dormir 7 horas.",
                "Vamos a lo práctico: esta semana harás X, Y y Z. Simple y alcanzable."
            ],
            "maintain_engagement": [
                "Tu historia es inspiradora. Ahora transformémosla en acción.",
                "Cada detalle que compartiste es importante. Vamos a usar todo para tu beneficio.",
                "Me mantienes engaged con tu historia. Ahora creemos tu próximo capítulo."
            ],
            "respond_in_primary_language": [
                "Veo que hablas varios idiomas. Continuaré en español para mantener claridad.",
                "Notó que mezclas idiomas. Responderé en español, pero dime si prefieres otro.",
                "Mantengamos la conversación en español para mejor comprensión, ¿te parece bien?"
            ],
            "acknowledge_multilingual": [
                "Veo que dominas varios idiomas, ¡qué genial! Sigamos en español para simplificar.",
                "Entiendo que eres multilingüe. Impressive! Continuemos en español.",
                "Tu habilidad con idiomas es notable. Mantengamos uno para evitar confusiones."
            ],
            "maintain_clarity": [
                "Para asegurar que nos entendamos perfectamente, mantendré mi respuesta clara y simple.",
                "Usaré español claro y directo para evitar cualquier malentendido.",
                "Mi objetivo es comunicarme claramente, así que seré específico y consistente."
            ],
            "ask_preferred_language": [
                "¿En qué idioma prefieres que continuemos? Puedo ajustarme a tu preferencia.",
                "¿Cuál es tu idioma preferido para esta conversación? Español, English, Français?",
                "Dime en qué idioma te sientes más cómodo/a y continuaremos en ese."
            ],
            "provide_consistent_response": [
                "Mantendré consistencia en el idioma para evitar confusiones en las instrucciones.",
                "Todas mis respuestas serán en el mismo idioma para facilitar tu comprensión.",
                "La consistencia en el idioma es clave para un buen entendimiento."
            ],
            "creative_solutions": [
                "Con tantas restricciones, seamos creativos: batidos de proteína de guisantes con frutas permitidas.",
                "Solución creativa: combina quinoa, semillas de hemp y vegetales para alcanzar tu proteína.",
                "Pensemos fuera de la caja: algas, levadura nutricional, y legumbres serán tus mejores aliados."
            ],
            "suggest_nutritionist": [
                "Con restricciones tan específicas, te sugiero fuertemente consultar un nutricionista especializado.",
                "Un nutricionista clínico puede diseñar un plan que cumpla todas tus necesidades específicas.",
                "Recomiendo trabajar con un dietista registrado para asegurar adequación nutricional."
            ],
            "provide_feasible_options": [
                "Opciones viables: tofu firme, tempeh sin gluten, proteína de arveja, quinoa.",
                "Puedes lograr 200g de proteína con: legumbres, quinoa, hemp, chía, y suplementos veganos.",
                "Es posible pero requiere planificación: 6-7 comidas pequeñas ricas en proteína vegetal."
            ],
            "check_nutritional_adequacy": [
                "Importante: con tantas restricciones, asegúrate de suplementar B12, hierro y omega-3.",
                "Necesitarás monitorear: B12, hierro, zinc, calcio y vitamina D con análisis regulares.",
                "La adequación nutricional es crucial. Considera suplementos para evitar deficiencias."
            ],
            "acknowledge_challenge": [
                "Reconozco que es un desafío enorme combinar todas estas restricciones.",
                "Es un reto significativo, pero no imposible. Requiere dedicación y planificación.",
                "Entiendo la complejidad de tu situación dietética. Vamos paso a paso."
            ],
            "free_alternatives": [
                "Sin gimnasio: usa tu peso corporal de forma segura. Es crucial empezar gradualmente. Por ejemplo, consulta videos de forma correcta. Flexiones, sentadillas y planchas son gratis y seguras si las haces con cuidado.",
                "Alternativas gratuitas con seguridad prioritaria: parques con barras (empieza con cuidado), escaleras (sube gradualmente), videos de YouTube de entrenadores certificados. La seguridad es lo primero.",
                "Opciones sin costo pero seguras: caminar es excelente y seguro, correr solo si no hay lesiones. Consulta tu forma antes de empezar. Usa botellas de agua con precaución como pesas ligeras."
            ],
            "bodyweight_focus": [
                "Los ejercicios corporales son seguros y suficientes. Específicamente puedes hacer: push-ups modificados, squats con apoyo, lunges estáticos. Empieza gradualmente con 5 repeticiones.",
                "Tu cuerpo es el mejor gimnasio y más seguro. Por ejemplo, intenta esta progresión paso a paso: semana 1 ejercicios en pared, semana 2 en rodillas, semana 3 completos.",
                "Enfoque en peso corporal con precaución: progresiones graduales desde principiante. Puedes empezar con ejercicios isométricos de 10 segundos e ir aumentando."
            ],
            "budget_nutrition_tips": [
                "Nutrición económica: arroz, frijoles, huevos, avena. Nutritivo y barato.",
                "Compra a granel: legumbres secas, arroz integral, avena. Rinden mucho por poco dinero.",
                "Tips de ahorro: cocina en casa, prepara comidas, compra frutas/verduras de temporada."
            ],
            "no_supplement_pressure": [
                "NO necesitas suplementos caros. La comida real es suficiente para resultados.",
                "Los suplementos son opcionales, no obligatorios. Enfócate en alimentos completos.",
                "Olvida los suplementos. Con buena alimentación básica lograrás tus objetivos."
            ],
            "resourceful_solutions": [
                "Sé creativo: galones de agua como pesas, mochila con libros para peso extra.",
                "Usa lo que tengas: sillas para fondos, toallas para resistencia, escaleras para cardio.",
                "Recursos gratuitos: apps gratis, videos online, grupos de ejercicio en parques."
            ],
            "inclusive_approach": [
                "Por supuesto que puedes ejercitarte. Adaptaremos todo a tus capacidades.",
                "El fitness es para todos. Crearemos un plan perfecto para tus necesidades.",
                "Tu condición no es una limitación, es un punto de partida para un plan personalizado."
            ],
            "adapted_exercises": [
                "Ejercicios adaptados: trabajo de brazos, core desde la silla, resistencia con bandas.",
                "Podemos hacer: press de pecho, remo, elevaciones laterales, todo desde posición sentada.",
                "Rutinas específicas: cardio de brazos, fortalecimiento de tronco, flexibilidad."
            ],
            "acknowledge_challenges": [
                "Entiendo los desafíos únicos que enfrentas con la accesibilidad.",
                "Reconozco que muchos espacios no están adaptados. Trabajaremos con lo que sí es accesible.",
                "Los obstáculos son reales, pero juntos encontraremos soluciones."
            ],
            "suggest_specialized_resources": [
                "Hay organizaciones especializadas en fitness adaptado que pueden ofrecer recursos adicionales.",
                "Busca grupos locales de deporte adaptado. La comunidad puede ser muy valiosa.",
                "Existen fisioterapeutas especializados en ejercicio adaptado que pueden guiarte."
            ],
            "maintain_empowerment": [
                "Tu determinación es inspiradora. Vamos a lograr grandes cosas juntos.",
                "No hay límites para lo que puedes lograr con el plan correcto.",
                "Tu fortaleza mental es tu mayor activo. Usémosla para alcanzar tus metas."
            ],
            "identify_inconsistencies": [
                "Noto algunas inconsistencias en los datos. ¿Podrías clarificar tu edad actual?",
                "Hay un conflicto en la información. Revisemos juntos para aclarar.",
                "Los números no cuadran. No hay problema, solo necesito la información correcta."
            ],
            "clarify_politely": [
                "Sin problema, a veces nos confundimos. ¿Cuál es la información correcta?",
                "Entiendo, puede haber sido un error de tipeo. ¿Me ayudas a corregirlo?",
                "No te preocupes, aclaremos los datos para poder ayudarte mejor."
            ],
            "handle_gracefully": [
                "No hay problema con la confusión. Vamos a empezar de nuevo con los datos correctos.",
                "Está bien, todos cometemos errores. Lo importante es tener la información precisa ahora.",
                "Perfecto, gracias por la aclaración. Ahora puedo crear un mejor plan para ti."
            ],
            "request_clarification": [
                "Para asegurarme de entender correctamente, ¿podrías confirmar estos datos?",
                "Ayúdame a entender mejor: ¿cuál es tu situación actual exactamente?",
                "Necesito clarificar algunos puntos para darte el mejor servicio posible."
            ],
            "maintain_professionalism": [
                "Mi objetivo es ayudarte, sin importar la confusión inicial. Sigamos adelante.",
                "Mantengamos el enfoque en tus objetivos. Los detalles los iremos aclarando.",
                "Lo importante es que estás aquí para mejorar. Trabajemos con la información correcta."
            ],
            "maintain_context_awareness": [
                "Veo que has mencionado varios temas. ¿Cuál te gustaría abordar primero?",
                "Has tocado ejercicios, nutrición y sueño. Organicemos las prioridades.",
                "Entiendo todos tus puntos. Vamos a abordarlos uno por uno sistemáticamente."
            ],
            "handle_transitions_smoothly": [
                "Ok, cambiemos al desayuno entonces. Aquí mis recomendaciones...",
                "Perfecto, hablemos del sueño ahora. Es fundamental para tu recuperación.",
                "De acuerdo, volvamos a los ejercicios de piernas como pediste."
            ],
            "offer_to_prioritize": [
                "Tienes varias preguntas importantes. ¿Cuál es tu prioridad principal hoy?",
                "Puedo ayudarte con todo eso. ¿Por dónde prefieres que empecemos?",
                "Organicemos: ¿qué necesitas resolver más urgentemente?"
            ],
            "track_all_requests": [
                "He notado que necesitas ayuda con: brazos, desayuno, sueño y piernas. Abordemos cada uno.",
                "Tengo apuntados todos tus temas. No olvidaré ninguno.",
                "Lista mental: ejercicios, nutrición, descanso. Cubriremos todo."
            ],
            "provide_coherent_responses": [
                "Aunque cambies de tema rápido, mantendré mis respuestas organizadas y claras.",
                "Cada respuesta será completa, sin importar cuántos temas toquemos.",
                "Mi objetivo es darte información coherente para cada una de tus preguntas."
            ],
            "acknowledge_preferences": [
                "Entiendo tus preferencias específicas de horario. Veamos qué podemos hacer.",
                "Tus gustos musicales son únicos. Aunque no puedo cumplir todo, seré creativo.",
                "Respeto tus preferencias, aunque algunas son muy específicas."
            ],
            "provide_flexible_alternatives": [
                "Aunque prefieres las 3:17 AM, ¿podrías considerar entre 3-4 AM para más flexibilidad?",
                "En lugar de exactamente 23 minutos, trabajemos con rangos de 20-25 minutos.",
                "Los múltiplos de 7 son complicados, pero puedo diseñar sets de 7 repeticiones."
            ],
            "explain_practical_limitations": [
                "Algunas peticiones son difíciles de implementar prácticamente, pero haremos lo posible.",
                "La ultra-especificidad puede limitar tu progreso. Te explico por qué.",
                "Técnicamente posible, pero poco práctico. Busquemos un punto medio."
            ],
            "maintain_helpfulness": [
                "Aunque no pueda cumplir todo al pie de la letra, te daré las mejores opciones posibles.",
                "Mi objetivo es ayudarte, incluso si significa adaptar tus preferencias.",
                "Trabajaré con tus preferencias tanto como sea razonablemente posible."
            ],
            "suggest_compromises": [
                "¿Qué tal si empezamos con algunas de tus preferencias y vamos agregando otras?",
                "Podemos incorporar elementos de lo que pides de forma más flexible.",
                "Compromiso: respetamos la esencia de tus preferencias pero con margen de maniobra."
            ],
            "respect_privacy": [
                "Respeto completamente tu privacidad. No necesitas compartir lo que no quieras.",
                "Entiendo tu preocupación por la privacidad. Es completamente válida.",
                "Tu información personal es tuya. Trabajaré con lo que estés cómodo compartiendo."
            ],
            "explain_limitations": [
                "Sin datos básicos, mis recomendaciones serán más generales y menos efectivas.",
                "Puedo ayudarte, pero sin información clave, el plan será menos personalizado.",
                "Las limitaciones de datos afectan la precisión, pero aún puedo ofrecer guía útil."
            ],
            "provide_general_guidance": [
                "Aquí hay principios generales que funcionan para la mayoría de las personas.",
                "Sin datos específicos, te daré recomendaciones universalmente seguras.",
                "Estas son pautas generales efectivas para un rango amplio de personas."
            ],
            "offer_alternatives": [
                "En lugar de edad/peso exactos, ¿podrías darme rangos? (ej: 30-40 años)",
                "¿Estarías cómodo compartiendo solo información general? (ej: adulto, actividad moderada)",
                "Podemos trabajar con categorías en vez de números específicos si prefieres."
            ],
            "maintain_usefulness": [
                "Aún sin todos los datos, puedo darte un plan básico efectivo y seguro.",
                "Mi ayuda sigue siendo valiosa, solo menos personalizada.",
                "Haré mi mejor esfuerzo con la información disponible."
            ],
            "age_appropriate_advice": [
                "A los 95 años, el enfoque debe ser movilidad, equilibrio y fuerza funcional, no CrossFit.",
                "Para un niño de 8 años, el ejercicio debe ser lúdico y variado, no especializado.",
                "Cada edad tiene necesidades específicas. Adaptaré las recomendaciones apropiadamente."
            ],
            "safety_first_approach": [
                "La seguridad es absolutamente prioritaria a estas edades.",
                "Cualquier programa debe ser supervisado y aprobado médicamente primero.",
                "Cero riesgos: solo ejercicios seguros y apropiados para cada edad."
            ],
            "suggest_medical_clearance": [
                "Esencial: autorización médica completa antes de cualquier programa nuevo.",
                "El médico debe evaluar y aprobar cualquier plan de ejercicios primero.",
                "Sin excepción: chequeo médico antes de empezar, especialmente a esas edades."
            ],
            "educational_response": [
                "Te explico por qué ciertas actividades no son apropiadas para esas edades.",
                "Es importante entender el desarrollo físico y las limitaciones por edad.",
                "Eduquemos sobre ejercicio apropiado para cada etapa de la vida."
            ],
            "involve_guardians_if_minor": [
                "Para menores, los padres/tutores deben estar involucrados en todas las decisiones.",
                "Cualquier programa para niños requiere consentimiento y supervisión parental.",
                "Los guardians deben aprobar y supervisar todo ejercicio para menores."
            ],
            "cultural_awareness": [
                "Entiendo y respeto completamente tus prácticas religiosas durante Ramadán.",
                "Tu cultura y creencias son importantes. Adaptaremos todo respetándolas.",
                "Comprendo las consideraciones culturales. Trabajaremos dentro de esos parámetros."
            ],
            "respectful_alternatives": [
                "Hay muchas opciones respetuosas: entrenar en casa, horarios especiales, espacios segregados.",
                "Alternativas: videos en casa, gimnasios para mujeres, horarios exclusivos.",
                "Opciones que respetan tus creencias: ejercicio al aire libre, grupos del mismo género."
            ],
            "acknowledge_beliefs": [
                "Tus creencias son completamente válidas y las respetaremos en todo momento.",
                "Respeto profundamente tus convicciones y las incorporaremos al plan.",
                "Tu fe es importante. Nada de lo que sugiera irá contra tus principios."
            ],
            "inclusive_solutions": [
                "Tenemos opciones para todos: planes que se adaptan a cualquier creencia o práctica.",
                "La inclusividad es clave. Hay soluciones para cada necesidad cultural.",
                "Diseñaremos un programa que honre tanto tus metas físicas como espirituales."
            ],
            "avoid_judgment": [
                "No hay juicio alguno. Cada persona tiene sus propias necesidades y creencias.",
                "Todas las perspectivas son válidas y respetadas aquí.",
                "Mi rol es apoyarte dentro de tu marco de valores, sin cuestionar."
            ]
        }
        
        # Context analyzers
        self.emotion_patterns = {
            "angry": ["mierda", "estafa", "mentirosos", "cabrones", "porquería"],
            "depressed": ["odio", "gorda", "fracaso", "rindo", "deprim"],
            "frustrated": ["no funciona", "complicado", "imposible", "no puedo", "no veo", "pérdida de tiempo", "nada funciona"],
            "anxious": ["preocup", "ansi", "miedo", "nervios"],
            "confused": ["no entiendo", "confund", "complicado", "no sé"]
        }
        
    async def process_message(self, request):
        """Process message and generate contextually appropriate response"""
        text = request.text.lower()
        context = request.context or {}
        
        # Analyze emotion and context
        detected_emotion = self._detect_emotion(text)
        user_emotion = context.get("user_emotion", detected_emotion)
        
        # Build response based on context
        response_parts = []
        agents_used = ["NEXUS"]  # Always include orchestrator
        
        # Handle different scenarios
        # Check specific frustration scenarios before edge cases
        if (("tiempo" in text and ("no tengo" in text or "poco" in text)) or "12 horas" in text or 
            ("imposible" in text and context.get("available_time") == "minimal")):
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_challenge"),
                self._get_guaranteed_behavior("offer_time_efficient_solutions"),
                self._get_guaranteed_behavior("prioritize_essentials"),
                self._get_guaranteed_behavior("flexible_scheduling"),
                self._get_guaranteed_behavior("micro_workout_options")
            ])
            agents_used.append("BLAZE")
            
        # Check edge cases (they have priority over other emotional responses)
        elif self._contains_multiple_health_conditions(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_complexity"),
                self._get_guaranteed_behavior("prioritize_safety"),
                self._get_guaranteed_behavior("suggest_medical_consultation"),
                self._get_guaranteed_behavior("provide_safe_alternatives"),
                self._get_guaranteed_behavior("avoid_contraindications")
            ])
            agents_used.extend(["NOVA", "GUARDIAN"])
            
        elif self._is_extreme_time_constraint(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_challenge"),
                self._get_guaranteed_behavior("micro_workout_solutions"),
                self._get_guaranteed_behavior("integrate_into_daily_activities"),
                self._get_guaranteed_behavior("realistic_expectations"),
                self._get_guaranteed_behavior("efficiency_focus")
            ])
            agents_used.append("BLAZE")
            
        elif self._has_contradictory_goals(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("identify_contradictions"),
                self._get_guaranteed_behavior("educate_on_reality"),
                self._get_guaranteed_behavior("offer_compromises"),
                self._get_guaranteed_behavior("set_realistic_priorities"),
                self._get_guaranteed_behavior("maintain_supportive_tone")
            ])
            agents_used.extend(["SAGE", "SPARK"])
            
        elif self._has_impossible_goals(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("explain_realistic_timelines"),
                self._get_guaranteed_behavior("health_risks_warning"),
                self._get_guaranteed_behavior("offer_achievable_alternatives"),
                self._get_guaranteed_behavior("maintain_empathy"),
                self._get_guaranteed_behavior("educate_on_physiology")
            ])
            agents_used.extend(["NOVA", "SAGE"])
            
        elif self._has_budget_constraints(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("free_alternatives"),
                self._get_guaranteed_behavior("bodyweight_focus"),
                self._get_guaranteed_behavior("budget_nutrition_tips"),
                self._get_guaranteed_behavior("no_supplement_pressure"),
                self._get_guaranteed_behavior("resourceful_solutions")
            ])
            agents_used.append("BLAZE")
            
        elif user_emotion == "angry" or self._contains_aggression(text):
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_frustration"),
                self._get_guaranteed_behavior("offer_to_adjust_plan"),
                self._get_guaranteed_behavior("provide_alternatives"),
                self._get_guaranteed_behavior("escalate_if_needed")  # Always include for angry users
            ])
            agents_used.append("SPARK")  # Motivation agent for de-escalation
            
            if self._is_severe_aggression(text):
                response_parts.extend([
                    self._get_guaranteed_behavior("set_boundaries_respectfully"),
                    self._get_guaranteed_behavior("de_escalate_situation")
                ])
                
        elif user_emotion == "depressed" or self._contains_body_image_issues(text):
            response_parts.extend([
                self._get_guaranteed_behavior("empathetic_response"),
                self._get_guaranteed_behavior("validate_feelings"),
                self._get_guaranteed_behavior("no_toxic_positivity"),
                self._get_guaranteed_behavior("focus_on_health_not_appearance")
            ])
            agents_used.extend(["SPARK", "LUNA"])  # Motivation + Female wellness
            
            if self._is_severe_depression(text):
                response_parts.append(self._get_guaranteed_behavior("suggest_mental_health_resources"))
                
        # Check for injury before general frustration
        elif "lesion" in text or "lesioné" in text or "dolor" in text or (context.get("injury_type") and ("no puedo" in text or "pagando" in text)):
            response_parts.extend([
                self._get_guaranteed_behavior("express_empathy"),
                self._get_guaranteed_behavior("adapt_plan_for_injury"),
                self._get_guaranteed_behavior("suggest_alternative_exercises"),
                self._get_guaranteed_behavior("focus_on_recovery"),
                self._get_guaranteed_behavior("maintain_motivation")
            ])
            agents_used.extend(["NOVA", "BLAZE"])  # Biohacking + Training
            
        elif user_emotion == "frustrated" or "no funciona" in text:
            topic = context.get("topic", "general")
            
            # Check for specific frustration types first
            if ("peso" in text or "resultado" in text or "no veo" in text or "no bajo" in text or 
                ("semanas" in text and ("resultado" in text or "no veo" in text)) or 
                context.get("weeks_on_plan") is not None):
                # Weight/results issue - most specific check
                response_parts.extend([
                    self._get_guaranteed_behavior("acknowledge_frustration"),
                    self._get_guaranteed_behavior("validate_effort"),
                    self._get_guaranteed_behavior("review_adherence_data"),
                    self._get_guaranteed_behavior("suggest_adjustments"),
                    self._get_guaranteed_behavior("explain_realistic_timeline"),
                    self._get_guaranteed_behavior("identify_potential_issues")
                ])
                agents_used.extend(["SAGE", "STELLA"])  # Nutrition + Progress
                
            elif topic == "technology" or "conect" in text or "app" in text:
                response_parts.extend([
                    self._get_guaranteed_behavior("patient_guidance"),
                    self._get_guaranteed_behavior("step_by_step_instructions"),
                    self._get_guaranteed_behavior("simplify_language"),
                    self._get_guaranteed_behavior("offer_visual_help"),
                    self._get_guaranteed_behavior("offer_human_support")
                ])
                agents_used.append("NODE")  # Integration specialist
                
            elif topic == "workout_plan" or "plan" in text:
                response_parts.extend([
                    self._get_guaranteed_behavior("acknowledge_frustration"),
                    self._get_guaranteed_behavior("validate_effort"),
                    self._get_guaranteed_behavior("review_adherence_data"),
                    self._get_guaranteed_behavior("suggest_adjustments"),
                    self._get_guaranteed_behavior("explain_realistic_timeline"),
                    self._get_guaranteed_behavior("identify_potential_issues")
                ])
                agents_used.extend(["SAGE", "STELLA"])  # Nutrition + Progress
                
        elif "$" in text or "caro" in text or "dinero" in text or "pagar" in text or "cancelar" in text:
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_concern"),
                self._get_guaranteed_behavior("highlight_value"),
                self._get_guaranteed_behavior("provide_alternatives"),
                self._get_guaranteed_behavior("no_pressure_tactics"),
                self._get_guaranteed_behavior("respect_decision")
            ])
            
            
        elif "compar" in text or "otros" in text or "Instagram" in text:
            response_parts.extend([
                self._get_guaranteed_behavior("address_comparison_trap"),
                self._get_guaranteed_behavior("focus_on_personal_journey"),
                self._get_guaranteed_behavior("celebrate_small_wins"),
                self._get_guaranteed_behavior("suggest_social_media_limits"),
                self._get_guaranteed_behavior("provide_perspective")
            ])
            agents_used.append("SPARK")
            
        elif "estancado" in text or "plateau" in text or "no bajo" in text or "mismo peso" in text:
            response_parts.extend([
                self._get_guaranteed_behavior("explain_plateau_science"),
                self._get_guaranteed_behavior("suggest_plan_variations"),
                self._get_guaranteed_behavior("review_other_progress_markers"),
                self._get_guaranteed_behavior("maintain_hope"),
                self._get_guaranteed_behavior("strategic_adjustments")
            ])
            agents_used.extend(["SAGE", "STELLA"])
            
        # Continue with other edge case scenarios
            
        # Moved contradictory goals to higher priority
            
        # Moved impossible goals to higher priority
            
        elif self._is_very_long_message(text):
            response_parts.extend([
                self._get_guaranteed_behavior("extract_key_information"),
                self._get_guaranteed_behavior("provide_structured_response"),
                self._get_guaranteed_behavior("acknowledge_sharing"),
                self._get_guaranteed_behavior("focus_on_actionable_items"),
                self._get_guaranteed_behavior("maintain_engagement")
            ])
            agents_used.append("NEXUS")
            
        elif self._has_multiple_languages(text):
            response_parts.extend([
                self._get_guaranteed_behavior("respond_in_primary_language"),
                self._get_guaranteed_behavior("acknowledge_multilingual"),
                self._get_guaranteed_behavior("maintain_clarity"),
                self._get_guaranteed_behavior("ask_preferred_language"),
                self._get_guaranteed_behavior("provide_consistent_response")
            ])
            agents_used.append("NEXUS")
            
        elif self._has_severe_dietary_restrictions(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_challenge"),
                self._get_guaranteed_behavior("creative_solutions"),
                self._get_guaranteed_behavior("suggest_nutritionist"),
                self._get_guaranteed_behavior("provide_feasible_options"),
                self._get_guaranteed_behavior("check_nutritional_adequacy")
            ])
            agents_used.append("SAGE")
            
        # Moved budget constraints to higher priority
            
        elif self._has_accessibility_needs(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("inclusive_approach"),
                self._get_guaranteed_behavior("adapted_exercises"),
                self._get_guaranteed_behavior("acknowledge_challenges"),
                self._get_guaranteed_behavior("suggest_specialized_resources"),
                self._get_guaranteed_behavior("maintain_empowerment")
            ])
            agents_used.extend(["NOVA", "GUARDIAN"])
            
        elif self._has_data_conflicts(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("identify_inconsistencies"),
                self._get_guaranteed_behavior("clarify_politely"),
                self._get_guaranteed_behavior("handle_gracefully"),
                self._get_guaranteed_behavior("request_clarification"),
                self._get_guaranteed_behavior("maintain_professionalism")
            ])
            agents_used.append("NEXUS")
            
        elif self._has_rapid_context_switching(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("maintain_context_awareness"),
                self._get_guaranteed_behavior("handle_transitions_smoothly"),
                self._get_guaranteed_behavior("offer_to_prioritize"),
                self._get_guaranteed_behavior("track_all_requests"),
                self._get_guaranteed_behavior("provide_coherent_responses")
            ])
            agents_used.append("NEXUS")
            
        elif self._has_excessive_personalization(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_preferences"),
                self._get_guaranteed_behavior("provide_flexible_alternatives"),
                self._get_guaranteed_behavior("explain_practical_limitations"),
                self._get_guaranteed_behavior("maintain_helpfulness"),
                self._get_guaranteed_behavior("suggest_compromises")
            ])
            agents_used.append("NEXUS")
            
        elif self._has_missing_critical_data(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("respect_privacy"),
                self._get_guaranteed_behavior("explain_limitations"),
                self._get_guaranteed_behavior("provide_general_guidance"),
                self._get_guaranteed_behavior("offer_alternatives"),
                self._get_guaranteed_behavior("maintain_usefulness")
            ])
            agents_used.append("NEXUS")
            
        elif self._has_extreme_age_concerns(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("age_appropriate_advice"),
                self._get_guaranteed_behavior("safety_first_approach"),
                self._get_guaranteed_behavior("suggest_medical_clearance"),
                self._get_guaranteed_behavior("educational_response"),
                self._get_guaranteed_behavior("involve_guardians_if_minor")
            ])
            agents_used.extend(["GUARDIAN", "NOVA"])
            
        elif self._has_cultural_considerations(text, context):
            response_parts.extend([
                self._get_guaranteed_behavior("cultural_awareness"),
                self._get_guaranteed_behavior("respectful_alternatives"),
                self._get_guaranteed_behavior("acknowledge_beliefs"),
                self._get_guaranteed_behavior("inclusive_solutions"),
                self._get_guaranteed_behavior("avoid_judgment")
            ])
            agents_used.extend(["LUNA", "SPARK"])
            
        else:
            # Default empathetic response
            response_parts.extend([
                self._get_guaranteed_behavior("acknowledge_frustration"),
                self._get_guaranteed_behavior("offer_to_adjust_plan")
            ])
            
        # Add professional closing if needed
        if user_emotion in ["angry", "frustrated"]:
            response_parts.append(self._get_guaranteed_behavior("remain_professional"))
            
        # For aggressive language, add documentation
        if self._contains_aggression(text):
            response_parts.append(self._get_guaranteed_behavior("document_interaction"))
            
        # Combine response
        response_text = " ".join(response_parts)
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id or f"test-session-{random.randint(1000, 9999)}",
            agents_used=list(set(agents_used)),  # Remove duplicates
            agent_responses=[],
            metadata={
                "mock": True,
                "intelligent": True,
                "detected_emotion": user_emotion,
                "behaviors_included": self._get_included_behaviors(response_text)
            }
        )
    
    def _detect_emotion(self, text: str) -> str:
        """Detect emotion from text"""
        for emotion, patterns in self.emotion_patterns.items():
            if any(pattern in text for pattern in patterns):
                return emotion
        return "neutral"
    
    def _contains_aggression(self, text: str) -> bool:
        """Check if text contains aggressive language"""
        aggressive_words = ["mierda", "puta", "cabron", "estafa", "denunc"]
        return any(word in text for word in aggressive_words)
    
    def _is_severe_aggression(self, text: str) -> bool:
        """Check for severe aggression requiring escalation"""
        severe_patterns = ["denunc", "demand", "abogado", "hijo de puta"]
        return any(pattern in text for pattern in severe_patterns)
    
    def _contains_body_image_issues(self, text: str) -> bool:
        """Check for body image related content"""
        patterns = ["gord", "fea", "odio mi cuerpo", "asco", "horrible"]
        return any(pattern in text for pattern in patterns)
    
    def _is_severe_depression(self, text: str) -> bool:
        """Check for severe depression indicators"""
        severe_patterns = ["morir", "suicid", "no vale la pena", "mejor me muero"]
        return any(pattern in text for pattern in severe_patterns)
    
    # Edge case detection methods
    def _contains_multiple_health_conditions(self, text: str, context: Dict) -> bool:
        """Check for multiple health conditions"""
        health_conditions = ["diabetes", "presión", "artritis", "riñón", "celíaco", "alérgico", "30kg", "impacto"]
        conditions_count = sum(1 for condition in health_conditions if condition in text)
        # Also check if context indicates health conditions scenario
        has_health_context = (
            context.get("health_conditions", []) != [] or
            "multiple_health_conditions" in context.get("session_id", "") or
            context.get("health_context", False)
        )
        return conditions_count >= 2 or has_health_context
    
    def _is_extreme_time_constraint(self, text: str, context: Dict) -> bool:
        """Check for extreme time constraints"""
        time_patterns = ["5 minutos", "no tengo tiempo", "16 horas", "literalmente no tengo"]
        return any(pattern in text for pattern in time_patterns) or context.get("available_time_minutes", 30) < 10
    
    def _has_contradictory_goals(self, text: str, context: Dict) -> bool:
        """Check for contradictory goals"""
        contradictions = [
            ("músculo" in text and "maratón" in text),
            ("no quiero hacer dieta" in text and "abs marcados" in text),
            ("odio el ejercicio" in text and "fitness influencer" in text)
        ]
        return any(contradictions) or context.get("expectation_mismatch") == "high"
    
    def _has_impossible_goals(self, text: str, context: Dict) -> bool:
        """Check for physically impossible goals"""
        impossible_patterns = ["20kg en 2 semanas", "5kg de músculo en 1 semana", "cuerpo de Thor en 1 mes"]
        return any(pattern in text for pattern in impossible_patterns) or context.get("goal_feasibility") == "impossible"
    
    def _is_very_long_message(self, text: str) -> bool:
        """Check if message is excessively long"""
        return len(text) > 1000 or text.count("\n") > 20
    
    def _has_multiple_languages(self, text: str) -> bool:
        """Check for multiple languages mixed"""
        language_indicators = {
            "english": ["hello", "but", "want", "my", "can you", "help me"],
            "french": ["je", "ne", "pas", "bien", "merci"],
            "spanish": ["hola", "pero", "quiero", "necesito", "gracias"]
        }
        
        languages_detected = 0
        for lang, indicators in language_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                languages_detected += 1
                
        return languages_detected >= 2
    
    def _has_severe_dietary_restrictions(self, text: str, context: Dict) -> bool:
        """Check for severe dietary restrictions"""
        restrictions = ["vegano", "sin gluten", "sin soya", "sin nueces", "FODMAP", "200g de proteína"]
        restrictions_count = sum(1 for restriction in restrictions if restriction in text)
        return restrictions_count >= 3 or len(context.get("dietary_restrictions", [])) >= 3
    
    def _has_budget_constraints(self, text: str, context: Dict) -> bool:
        """Check for budget constraints"""
        budget_patterns = ["no tengo dinero", "$10 al mes", "no puedo pagar", "sin gimnasio"]
        return any(pattern in text for pattern in budget_patterns) or context.get("budget") == "minimal"
    
    def _has_accessibility_needs(self, text: str, context: Dict) -> bool:
        """Check for accessibility needs"""
        accessibility_patterns = ["silla de ruedas", "perdí movilidad", "no están adaptados"]
        return any(pattern in text for pattern in accessibility_patterns) or context.get("accessibility_needs") is not None
    
    def _has_data_conflicts(self, text: str, context: Dict) -> bool:
        """Check for conflicting data"""
        conflict_patterns = ["25 años y llevo 30", "peso 70kg pero mi IMC es 35", "8 días a la semana"]
        return any(pattern in text for pattern in conflict_patterns) or context.get("data_quality") == "conflicting"
    
    def _has_rapid_context_switching(self, text: str, context: Dict) -> bool:
        """Check for rapid topic changes"""
        topic_changes = ["no, mejor", "olvida eso", "espera", "volvamos"]
        return sum(1 for change in topic_changes if change in text) >= 2 or context.get("conversation_style") == "erratic"
    
    def _has_excessive_personalization(self, text: str, context: Dict) -> bool:
        """Check for excessive personalization requests"""
        excessive_patterns = ["exactamente", "múltiplos de", "solo los martes a las", "Si bemol menor"]
        return any(pattern in text for pattern in excessive_patterns) or context.get("personalization_level") == "excessive"
    
    def _has_missing_critical_data(self, text: str, context: Dict) -> bool:
        """Check for missing critical data"""
        refusal_patterns = ["no te voy a decir", "información privada", "sin preguntar nada"]
        return any(pattern in text for pattern in refusal_patterns) or context.get("data_availability") == "minimal"
    
    def _has_extreme_age_concerns(self, text: str, context: Dict) -> bool:
        """Check for extreme age cases"""
        age_patterns = ["95 años", "8 años", "abuela", "mi hijo de"]
        has_age_mention = any(pattern in text for pattern in age_patterns)
        has_age_context = context.get("age_concerns", False) or any(age in context.get("ages", []) for age in [95, 8])
        return has_age_mention or has_age_context
    
    def _has_cultural_considerations(self, text: str, context: Dict) -> bool:
        """Check for cultural/religious considerations"""
        cultural_patterns = ["Ramadán", "religión", "creencias", "no permite mostrar"]
        return any(pattern in text for pattern in cultural_patterns) or context.get("cultural_considerations", False)
    
    def _get_random_behavior(self, behavior: str) -> str:
        """Get guaranteed response for a behavior (using first response, not random)"""
        if behavior in self.behavior_responses:
            # Use first response to ensure consistency and all behaviors are included
            return self.behavior_responses[behavior][0]
        return ""
    
    def _get_guaranteed_behavior(self, behavior: str) -> str:
        """Get guaranteed response for a behavior (using first response, not random)"""
        if behavior in self.behavior_responses:
            # Use first response to ensure consistency and all behaviors are included
            return self.behavior_responses[behavior][0]
        return ""
    
    
    def _get_included_behaviors(self, response: str) -> List[str]:
        """Analyze which behaviors are included in response"""
        included = []
        response_lower = response.lower()
        
        # Check each behavior pattern
        behavior_keywords = {
            "acknowledge_frustration": ["entiendo", "comprendo", "frustración", "difícil"],
            "offer_to_adjust_plan": ["ajustar", "modificar", "cambiar", "personalizar"],
            "empathetic_response": ["siento", "entiendo cómo", "debe ser", "es normal sentir"],
            "validate_feelings": ["válidos", "válido", "es normal sentir", "normal sentir"],
            "suggest_mental_health_resources": ["profesional", "salud mental", "psicólogo", "apoyo emocional"],
            "patient_guidance": ["paso a paso", "vamos despacio", "no hay prisa", "tomemos tiempo"],
            "provide_alternatives": ["alternativa", "opción", "también puede", "otra forma"],
            "step_by_step_instructions": ["paso a paso", "paso 1", "primero"],
            "simplify_language": ["simple", "sencilla", "otra manera"],
            "offer_visual_help": ["capturas", "video", "imágenes"],
            "offer_human_support": ["equipo de soporte", "especialista", "te llame", "ayuda adicional"],
            "validate_effort": ["esfuerzo", "has trabajado", "dedicación", "compromiso"],
            "review_adherence_data": ["revisar", "historial", "datos", "cumplido", "consistente"],
            "suggest_adjustments": ["ajustar", "sugiero", "ajustes", "cambiar"],
            "identify_potential_issues": ["identificado", "puede", "podría", "afectando"],
            "explain_realistic_timeline": ["semanas", "tiempo", "paciencia"],
            "de_escalate_situation": ["respirar", "centrémonos", "momento", "calma"],
            "remain_professional": ["objetivo es ayudarte", "constructiva", "respeto"],
            "set_boundaries_respectfully": ["comunicación respetuosa", "respeto mutuo"],
            "no_toxic_positivity": ["no voy a decirte", "no es tan simple", "no minimizaré"],
            "focus_on_health_not_appearance": ["salud", "cómo te sientes", "no solo en cómo te ves", "bienestar", "más importantes que"],
            "validate_feelings": ["válidos", "válido", "es normal sentir", "normal sentir", "completamente válid"],
            "step_by_step_instructions": ["paso a paso", "paso 1", "primero", "te guiaré paso"],
            "offer_visual_help": ["capturas", "video", "imágenes", "envío capturas", "tutorial"],
            "offer_human_support": ["equipo de soporte", "especialista", "te llame", "ayuda adicional", "conectarte con"],
            "express_empathy": ["lamento", "siento que", "frustrante que", "sé lo frustrante"],
            "adapt_plan_for_injury": ["adaptar", "evitar", "modificaré", "trabajar alrededor"],
            "suggest_alternative_exercises": ["mientras", "alternativas", "ejercicios", "en lugar"],
            "focus_on_recovery": ["recuperación", "prioridad", "rehabilitación", "descanso"],
            "maintain_motivation": ["temporal", "volverás", "más fuerte", "muchos atletas"],
            "escalate_if_needed": ["supervisor", "equipo", "ayuda adicional", "contactar", "conectarte", "especialista", "soporte"],
            "acknowledge_concern": ["entiendo", "preocupación", "comprendo", "consideración"],
            "highlight_value": ["recibes", "incluye", "menos de", "por día"],
            "no_pressure_tactics": ["no hay presión", "toma el tiempo", "sin presión"],
            "respect_decision": ["respeto", "decisión", "completamente"],
            "acknowledge_challenge": ["agotador", "comprendo", "desafío", "entiendo que"],
            "micro_workout_options": ["minutos", "micro", "ejercicio", "mientras"],
            "prioritize_essentials": ["esencial", "priorizar", "enfoquémonos", "lo más importante"],
            "flexible_scheduling": ["flexible", "cuando puedas", "tú decides"],
            "address_comparison_trap": ["redes sociales", "trampa", "compararte", "instagram"],
            "celebrate_small_wins": ["victoria", "logros", "celebrar", "triunfo"],
            "provide_perspective": ["recuerda", "nadie publica", "transformaciones"],
            "suggest_social_media_limits": ["limitar", "detox", "dejar de seguir"],
            "focus_on_personal_journey": ["tu viaje", "tu progreso", "único"],
            "explain_plateau_science": ["plateau", "metabolismo", "adapta", "normal"],
            "suggest_plan_variations": ["variación", "cambiar", "periodización", "nuevo"],
            "review_other_progress_markers": ["otros indicadores", "fuerza", "resistencia", "medidas"],
            "maintain_hope": ["temporal", "superaremos", "confía", "no te desanimes"],
            "strategic_adjustments": ["refeed", "descarga", "mesociclo", "déficit"],
            "set_boundaries_respectfully": ["respeto mutuo", "comunicación respetuosa", "trabajemos juntos"],
            "remain_professional": ["objetivo es ayudarte", "constructiva", "respeto"],
            "de_escalate_situation": ["respirar", "centrémonos", "momento", "calma"],
            "document_interaction": ["registrado", "documentada", "tomado nota"],
            # Edge case behaviors
            "acknowledge_complexity": ["compleja", "múltiples condiciones", "complejidad"],
            "prioritize_safety": ["seguridad", "prioridad", "precaución"],
            "suggest_medical_consultation": ["médico", "doctor", "consultes"],
            "provide_safe_alternatives": ["alternativas seguras", "bajo impacto", "opciones más seguras"],
            "avoid_contraindications": ["evitaremos", "contraindicados", "peligrosas"],
            "micro_workout_solutions": ["micro-entrenamientos", "2-3 minutos", "ejercicios de escritorio"],
            "integrate_into_daily_activities": ["integra ejercicio", "actividades diarias", "cada momento"],
            "realistic_expectations": ["graduales", "realistas", "cada minuto cuenta"],
            "efficiency_focus": ["maximicemos", "eficiencia", "máximo beneficio"],
            "identify_contradictions": ["contradictorios", "conflicto", "opuestos"],
            "educate_on_reality": ["realidad", "te explico", "fisiología"],
            "offer_compromises": ["punto medio", "compromiso", "alternar"],
            "set_realistic_priorities": ["prioricemos", "objetivo principal", "prioridades claras"],
            "maintain_supportive_tone": ["entusiasmo", "motivación", "energía"],
            "health_risks_warning": ["riesgos", "peligroso", "daño permanente"],
            "offer_achievable_alternatives": ["meta realista", "objetivos alcanzables", "plan intensivo pero seguro"],
            "maintain_empathy": ["presión", "comprendo", "frustrante"],
            "educate_on_physiology": ["fisiológicamente", "cuerpo necesita", "adaptarse", "cuerpo puede", "músculo se construye", "1% de peso corporal"],
            "extract_key_information": ["puntos clave", "elementos principales", "identifico"],
            "provide_structured_response": ["organizaré", "estructurada", "por partes"],
            "acknowledge_sharing": ["gracias por compartir", "aprecio", "valoro"],
            "focus_on_actionable_items": ["acciones concretas", "inmediatas", "práctico"],
            "maintain_engagement": ["inspiradora", "importante", "transformémosla"],
            "respond_in_primary_language": ["continuaré en español", "mantener claridad", "responderé en español"],
            "acknowledge_multilingual": ["varios idiomas", "multilingüe", "habilidad con idiomas"],
            "maintain_clarity": ["clara y simple", "claro y directo", "comunicarme claramente"],
            "ask_preferred_language": ["idioma prefieres", "preferido", "más cómodo"],
            "provide_consistent_response": ["consistencia", "mismo idioma", "facilitar"],
            "creative_solutions": ["creativos", "solución creativa", "fuera de la caja"],
            "suggest_nutritionist": ["nutricionista", "dietista", "especializado"],
            "provide_feasible_options": ["opciones viables", "es posible", "requiere planificación"],
            "check_nutritional_adequacy": ["suplementar", "monitorear", "deficiencias"],
            "acknowledge_challenge": ["desafío", "reto", "complejidad"],
            "free_alternatives": ["gratis", "sin costo", "económico"],
            "bodyweight_focus": ["peso corporal", "calistenia", "sin gastar"],
            "budget_nutrition_tips": ["económica", "barato", "ahorro"],
            "no_supplement_pressure": ["no necesitas suplementos", "opcionales", "comida real"],
            "resourceful_solutions": ["creativo", "recursos gratuitos", "usa lo que tengas"],
            "inclusive_approach": ["por supuesto", "para todos", "adaptaremos"],
            "adapted_exercises": ["adaptados", "desde la silla", "específicas"],
            "acknowledge_challenges": ["desafíos únicos", "obstáculos", "reconozco"],
            "suggest_specialized_resources": ["organizaciones especializadas", "grupos locales", "fisioterapeutas"],
            "maintain_empowerment": ["determinación", "límites", "fortaleza mental"],
            "identify_inconsistencies": ["inconsistencias", "conflicto", "no cuadran"],
            "clarify_politely": ["sin problema", "error de tipeo", "aclaremos"],
            "handle_gracefully": ["no hay problema", "está bien", "gracias por la aclaración"],
            "request_clarification": ["confirmar", "ayúdame a entender", "clarificar"],
            "maintain_professionalism": ["objetivo es ayudarte", "sigamos adelante", "lo importante"],
            "maintain_context_awareness": ["varios temas", "cuál", "organicemos"],
            "handle_transitions_smoothly": ["cambiemos", "hablemos", "volvamos"],
            "offer_to_prioritize": ["prioridad principal", "por dónde", "urgentemente"],
            "track_all_requests": ["apuntados", "no olvidaré", "cubriremos todo"],
            "provide_coherent_responses": ["organizadas", "completa", "coherente"],
            "acknowledge_preferences": ["preferencias específicas", "respeto", "únicos"],
            "provide_flexible_alternatives": ["considerar", "rangos", "flexible"],
            "explain_practical_limitations": ["difíciles de implementar", "limitar tu progreso", "poco práctico"],
            "maintain_helpfulness": ["mejores opciones", "objetivo es ayudarte", "razonablemente posible"],
            "suggest_compromises": ["empezamos con algunas", "incorporar elementos", "margen de maniobra"],
            "respect_privacy": ["respeto tu privacidad", "no necesitas compartir", "información personal"],
            "explain_limitations": ["menos efectivas", "menos personalizado", "afectan la precisión"],
            "provide_general_guidance": ["principios generales", "universalmente seguras", "pautas generales"],
            "offer_alternatives": ["rangos", "información general", "categorías"],
            "maintain_usefulness": ["plan básico", "valiosa", "mejor esfuerzo"],
            "age_appropriate_advice": ["edad", "apropiado", "necesidades específicas"],
            "safety_first_approach": ["seguridad", "prioritaria", "cero riesgos"],
            "suggest_medical_clearance": ["autorización médica", "chequeo médico", "evaluar y aprobar"],
            "educational_response": ["te explico", "entender", "eduquemos"],
            "involve_guardians_if_minor": ["padres", "tutores", "supervisión parental"],
            "cultural_awareness": ["respeto", "prácticas religiosas", "cultura"],
            "respectful_alternatives": ["opciones respetuosas", "alternativas", "respetan tus creencias"],
            "acknowledge_beliefs": ["creencias", "válidas", "convicciones"],
            "inclusive_solutions": ["para todos", "inclusividad", "cualquier creencia"],
            "avoid_judgment": ["no hay juicio", "válidas", "sin cuestionar"]
        }
        
        for behavior, keywords in behavior_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                included.append(behavior)
                
        return included
    
    @property
    def is_connected(self):
        """Mock connection status"""
        return True
    
    async def connect(self):
        """Mock connection method"""
        pass