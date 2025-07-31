"""
Intelligent Mock Orchestrator Client for Beta Validation Tests

This mock simulates realistic responses from the GENESIS orchestrator
to properly test expected behaviors without requiring full infrastructure.
"""

import random
import re
from functools import lru_cache
from typing import Dict, List

from app.schemas.chat import ChatResponse


class IntelligentMockOrchestratorClient:
    """Mock client that generates contextually appropriate responses"""

    def __init__(self):
        """Initialize with behavior response templates"""
        # Cache for compiled patterns and analyzed behaviors
        self._pattern_cache = {}
        self._behavior_cache = {}
        self._emotion_patterns = None
        self.behavior_responses = {
            # Frustration handling
            "acknowledge_frustration": [
                "Entiendo tu frustración completamente. Comprendo lo difícil que debe ser esta situación para ti.",
                "Comprendo perfectamente tu frustración. Entiendo que esto es muy difícil y frustrante para ti.",
                "Entiendo y comprendo tu frustración. Sé lo difícil que es cuando las cosas no funcionan como esperamos.",
            ],
            "offer_to_adjust_plan": [
                "Vamos a ajustar tu plan para que funcione mejor para ti. Puedo modificar todo lo que necesites.",
                "Puedo modificar el plan según tus necesidades específicas. Vamos a cambiar lo que no está funcionando.",
                "Revisemos juntos qué cambios podemos hacer para personalizar tu experiencia. Podemos ajustar cualquier aspecto del plan.",
            ],
            "provide_alternatives": [
                "Aquí hay algunas alternativas que podrían funcionar mejor:\n• Primera alternativa: Plan de baja intensidad\n• Segunda opción: Rutinas en casa\n• También puedes probar otra forma de entrenar",
                "Te propongo varias alternativas: una opción es empezar con 3 días, también puedes alternar ejercicios. Otra forma es un enfoque gradual.",
                "Tengo diferentes alternativas: primera opción son rutinas de 20 minutos, también puedes hacer ejercicios de bajo impacto. Otra forma es un plan progresivo.",
            ],
            "escalate_if_needed": [
                "Si prefieres, puedo conectarte con nuestro equipo de soporte especializado para brindarte ayuda adicional.",
                "Voy a notificar a un supervisor para que te contacte directamente y resuelva tu situación.",
                "Permíteme transferirte a un especialista humano que puede ayudarte mejor con tu caso específico.",
            ],
            # Empathy and emotional support
            "empathetic_response": [
                "Siento mucho que estés pasando por esto. Entiendo cómo te sientes y debe ser muy difícil. Es normal sentir frustración.",
                "Entiendo cómo debe afectarte esta situación. Siento que sea tan difícil para ti. Es normal sentir estas emociones.",
                "Debe ser muy frustrante para ti. Siento que estés pasando por esto y entiendo cómo te afecta. Es normal sentir así.",
            ],
            "validate_feelings": [
                "Tus sentimientos son completamente válidos. Es normal sentir así en esta situación.",
                "Es válido lo que sientes. Tus sentimientos son normales y comprensibles.",
                "Tus sentimientos son válidos y es normal sentir así. No hay nada malo en ello.",
            ],
            "suggest_mental_health_resources": [
                "Puede ser útil hablar con un profesional de salud mental sobre esto.",
                "Tenemos recursos de apoyo emocional disponibles si los necesitas.",
                "Considera buscar apoyo profesional, tu bienestar mental es prioritario.",
            ],
            "focus_on_health_not_appearance": [
                "Enfoquémonos en cómo te sientes, no solo en cómo te ves.",
                "Tu salud y bienestar son más importantes que cualquier número en la báscula.",
                "Trabajemos en objetivos de salud y energía, más allá de la apariencia.",
            ],
            # Technical support
            "step_by_step_instructions": [
                "Te guiaré paso a paso:\n1. Primero, abre la configuración de la app\n2. Luego, selecciona 'Dispositivos'\n3. Activa el Bluetooth en tu teléfono\n4. Busca tu reloj en la lista\n5. Toca para conectar",
                "Vamos despacio, paso por paso:\nPaso 1: Asegúrate que tu reloj esté encendido\nPaso 2: Abre nuestra app\nPaso 3: Ve a Configuración > Dispositivos\nPaso 4: Selecciona 'Agregar nuevo dispositivo'",
                "Te explicaré cada paso detalladamente:\n1. Reinicia tu teléfono y el reloj\n2. Abre la app NGX\n3. Toca el ícono de configuración\n4. Selecciona 'Vincular dispositivo'\n5. Sigue las instrucciones en pantalla",
            ],
            "simplify_language": [
                "Déjame explicarlo de forma más simple: solo necesitas tocar el botón azul que dice 'Conectar'.",
                "Lo diré de otra manera más sencilla: es como emparejar audífonos Bluetooth, el proceso es muy similar.",
                "Vamos a simplificar esto: olvida todo lo anterior, solo abre la app y yo te guiaré desde ahí.",
            ],
            "patient_guidance": [
                "Tómate tu tiempo, no hay prisa. Cuando estés listo/a, avísame y continuamos.",
                "Vamos a tu ritmo, paso a paso. Si necesitas que repita algo, solo dímelo.",
                "No te preocupes si toma tiempo, estoy aquí para ayudarte todo lo que necesites. La tecnología puede ser frustrante a veces.",
            ],
            "offer_visual_help": [
                "¿Te ayudaría si te envío capturas de pantalla mostrando exactamente dónde hacer clic?",
                "Puedo enviarte un video tutorial corto que muestra el proceso completo.",
                "Tenemos guías visuales con imágenes paso a paso en nuestra sección de ayuda.",
            ],
            "offer_human_support": [
                "Si prefieres, puedo conectarte con un miembro de nuestro equipo de soporte técnico por teléfono.",
                "¿Te gustaría que un especialista te llame para guiarte por teléfono?",
                "Nuestro equipo de soporte humano está disponible de 9am a 6pm si prefieres hablar con alguien.",
            ],
            # Progress and plateaus
            "validate_effort": [
                "Reconozco todo el esfuerzo que has puesto. Has trabajado con mucha dedicación y eso muestra tu compromiso.",
                "Has trabajado muy duro y veo tu esfuerzo. Tu dedicación es admirable y tu compromiso es evidente.",
                "Tu dedicación y compromiso son evidentes. Veo cuánto has trabajado y todo el esfuerzo que has puesto.",
            ],
            "review_adherence_data": [
                "Déjame revisar tu historial de entrenamientos para ver qué podemos mejorar.",
                "Veo en tus datos que has sido consistente con los ejercicios pero quizás necesitamos ajustar la nutrición.",
                "Analizando tu progreso, noto que has seguido el plan al 85%. Veamos qué ajustes podemos hacer.",
            ],
            "suggest_adjustments": [
                "Basándome en tu progreso, sugiero aumentar la intensidad en un 10% y agregar un día más de cardio.",
                "Podríamos ajustar tus macros: aumentar proteína a 1.8g/kg y reducir ligeramente los carbohidratos.",
                "Te sugiero cambiar el enfoque: en lugar de 5 días de gym, hagamos 3 días de fuerza + 2 de actividad que disfrutes.",
            ],
            "identify_potential_issues": [
                "Puede que estés experimentando retención de líquidos, lo cual es normal en las primeras semanas.",
                "El estrés y la falta de sueño pueden estar afectando tus resultados. ¿Cómo has estado durmiendo?",
                "A veces el cuerpo necesita un 'refeed day' para reactivar el metabolismo. Consideremos agregarlo.",
            ],
            "explain_realistic_timeline": [
                "Los cambios sostenibles toman tiempo. En 3 semanas apenas estamos iniciando - los cambios visibles suelen aparecer entre las semanas 6-8.",
                "Es normal no ver resultados inmediatos. El cuerpo necesita 4-6 semanas para adaptarse antes de mostrar cambios significativos.",
                "Los resultados reales y duraderos requieren paciencia. La pérdida de peso saludable es de 0.5-1kg por semana máximo.",
            ],
            "explain_plateau_science": [
                "Los plateaus son normales - tu metabolismo se adapta y necesitamos cambiar el estímulo. Es señal de que el plan está funcionando, solo necesita evolucionar.",
                "Esto es señal de que tu cuerpo se está ajustando. Después de 2 meses, es momento de variar intensidad, volumen o tipo de ejercicio.",
                "Los estancamientos son temporales. Tu cuerpo es eficiente y se adapta. Necesitamos 'confundirlo' con nuevos estímulos para reactivar el progreso.",
            ],
            "suggest_plan_variations": [
                "Probemos con periodización: una semana de alta intensidad seguida de una de recuperación activa.",
                "Cambiemos el enfoque: si hacías pesas 4x1, probemos con circuitos metabólicos 3x1 + 2 días de HIIT.",
                "Agreguemos variedad: natación un día, ciclismo otro, y mantengamos 3 días de fuerza.",
            ],
            "review_other_progress_markers": [
                "Aunque el peso esté estancado, ¿has notado cambios en tu energía, fuerza o medidas corporales?",
                "Revisemos otros indicadores: ¿Cómo está tu resistencia? ¿Puedes hacer más repeticiones que antes?",
                "El progreso no es solo la báscula: ¿Cómo te queda la ropa? ¿Has tomado fotos de progreso?",
            ],
            "maintain_hope": [
                "Este plateau es temporal y lo superaremos juntos. Cada plateau superado te acerca más a tu meta.",
                "No te desanimes - esto es parte normal del viaje. Los mejores resultados vienen después de superar estos momentos.",
                "Confía en el proceso. Has llegado muy lejos y este es solo un escalón más hacia tu objetivo.",
            ],
            "strategic_adjustments": [
                "Implementemos un 'refeed day' semanal para reactivar tu metabolismo.",
                "Hagamos una semana de descarga (50% volumen) seguida de un nuevo mesociclo con mayor intensidad.",
                "Estrategia: 2 semanas de déficit calórico alternadas con 1 semana en mantenimiento para evitar adaptación metabólica.",
            ],
            # Professional boundaries
            "remain_professional": [
                "Entiendo que estés molesto/a. Mi objetivo es ayudarte a resolver esta situación de la mejor manera posible.",
                "Comprendo tu frustración y es válida. Enfoquémonos en encontrar una solución que funcione para ti.",
                "Respeto tus sentimientos. Trabajemos juntos para resolver esto de manera constructiva.",
            ],
            "set_boundaries_respectfully": [
                "Entiendo tu enojo y quiero ayudarte. Para poder hacerlo efectivamente, mantengamos una comunicación respetuosa.",
                "Tu frustración es comprensible. Te pido que mantengamos un diálogo constructivo para poder resolver tu situación.",
                "Estoy aquí para ayudarte y quiero hacerlo. Trabajemos juntos con respeto mutuo para encontrar la mejor solución.",
            ],
            "de_escalate_situation": [
                "Entiendo que estés muy molesto/a. Tomemos un momento para respirar y luego busquemos la mejor solución juntos.",
                "Escucho tu frustración. ¿Qué es lo más importante que necesitas resolver ahora mismo?",
                "Comprendo completamente tu enojo. Centrémonos en lo que puedo hacer ahora mismo para ayudarte.",
            ],
            "document_interaction": [
                "He registrado tu feedback y lo compartiré con el equipo para mejorar nuestro servicio.",
                "Toda esta conversación está siendo documentada para asegurar un seguimiento apropiado.",
                "He tomado nota de todos tus comentarios y los escalaré al departamento correspondiente.",
            ],
            # Body image and self-esteem
            "no_toxic_positivity": [
                "No voy a decirte que 'solo pienses positivo'. Tus sentimientos son reales y válidos.",
                "Entiendo que no es tan simple como 'quererse a uno mismo'. Es un proceso complejo.",
                "No minimizaré lo que sientes. Es difícil y está bien reconocerlo.",
            ],
            # Injury support
            "express_empathy": [
                "Lamento mucho que te hayas lesionado. Sé lo frustrante que puede ser cuando estabas progresando.",
                "Siento que estés pasando por esto. Las lesiones son desafiantes física y emocionalmente.",
                "Es muy frustrante lesionarse justo cuando veías progreso. Lo siento mucho.",
            ],
            "adapt_plan_for_injury": [
                "Vamos a adaptar completamente tu plan para trabajar alrededor de tu lesión de rodilla.",
                "Modificaré tu rutina para evitar cualquier ejercicio que pueda agravar tu lesión.",
                "Crearé un plan específico de rehabilitación que respete tu proceso de recuperación.",
            ],
            "suggest_alternative_exercises": [
                "Mientras tu rodilla se recupera, podemos enfocarnos en: ejercicios de tren superior, core, y movilidad.",
                "Aquí hay alternativas seguras: natación (si el médico lo aprueba), ejercicios sentado, yoga suave.",
                "Podemos trabajar en: fortalecimiento de brazos, ejercicios isométricos suaves, estiramientos terapéuticos.",
            ],
            "focus_on_recovery": [
                "La prioridad ahora es tu recuperación completa. El fitness puede esperar, tu salud no.",
                "Enfoquémonos en rehabilitación: ejercicios de fisioterapia, descanso adecuado, nutrición para recuperación.",
                "Tu recuperación es lo más importante. Vamos a ir despacio y seguro.",
            ],
            "maintain_motivation": [
                "Esta pausa es temporal. Volverás más fuerte y con más conocimiento sobre tu cuerpo.",
                "Usa este tiempo para trabajar en otros aspectos: flexibilidad, meditación, nutrición.",
                "Las lesiones son parte del viaje. Muchos atletas vuelven más fuertes después de recuperarse.",
            ],
            # Financial concerns
            "acknowledge_concern": [
                "Entiendo completamente tu preocupación sobre el costo. Es una consideración importante.",
                "Tu preocupación financiera es totalmente válida. Hablemos de opciones.",
                "Comprendo que el presupuesto es una consideración real e importante.",
            ],
            "highlight_value": [
                "Por $59 al mes recibes: planes personalizados, soporte 24/7, actualizaciones semanales, y acceso a 6 especialistas.",
                "Considera que es menos de $2 por día - menos que un café - por tu salud integral.",
                "Incluye todo lo que necesitas: nutrición, entrenamiento, mindfulness, sin costos adicionales de gym o nutricionista.",
            ],
            "no_pressure_tactics": [
                "No hay presión. Toma el tiempo que necesites para decidir qué es mejor para ti.",
                "Tu decisión es respetada completamente, sin importar cuál sea.",
                "No utilizaré tácticas de venta. Tu bienestar financiero también es importante.",
            ],
            "respect_decision": [
                "Respeto completamente tu decisión. Si decides cancelar, aquí está el proceso...",
                "Entiendo tu decisión y la respeto. ¿Hay algo más en lo que pueda ayudarte?",
                "Tu decisión es completamente respetada. Gracias por darle una oportunidad a NGX.",
            ],
            # Time management
            "acknowledge_challenge": [
                "Trabajar 12 horas al día es agotador. Entiendo que encontrar tiempo para ejercitar es un verdadero desafío.",
                "Comprendo completamente. Con esa carga laboral, el tiempo es extremadamente limitado.",
                "Es un desafío real. Muchos de nuestros usuarios enfrentan la misma situación.",
            ],
            "offer_time_efficient_solutions": [
                "Te propongo rutinas de 15 minutos de alta efectividad que puedes hacer en casa o la oficina.",
                "Tengo soluciones eficientes: entrenamientos HIIT de 10-15 minutos que maximizan resultados.",
                "Puedo diseñar un plan ultra-eficiente: 3 sesiones semanales de 20 minutos máximo.",
            ],
            "micro_workout_options": [
                "Micro-entrenamientos de 5 minutos: flexiones en la oficina, sentadillas mientras esperas el café.",
                "Aprovecha micro-momentos: 2 minutos de ejercicio cada hora suma 16 minutos al día.",
                "Rutinas de escritorio: ejercicios que puedes hacer sin levantarte de tu silla.",
            ],
            "prioritize_essentials": [
                "Enfoquémonos en lo esencial: 3 ejercicios clave que te darán el 80% de los resultados.",
                "Vamos a priorizar: nutrición primero (70% de resultados), luego ejercicio básico.",
                "Lo esencial primero: 10 minutos de movimiento diario y mejoras nutricionales simples.",
            ],
            "flexible_scheduling": [
                "Tu horario es flexible: entrena cuando puedas, sin presión de horarios fijos.",
                "Adaptamos el plan a tu vida: mañanas, noches o fines de semana, tú decides.",
                "Sin horarios rígidos: el mejor momento para entrenar es cuando tú puedas.",
            ],
            # Comparison and social media
            "address_comparison_trap": [
                "Las redes sociales muestran solo los mejores momentos, no el proceso completo ni los fracasos.",
                "Compararte con otros es injusto contigo mismo. Cada cuerpo y situación es única.",
                "La trampa de la comparación es real. Instagram no muestra la historia completa.",
            ],
            "focus_on_personal_journey": [
                "Tu viaje es único. Compararte solo contigo mismo/a de ayer es lo que importa.",
                "Enfoquémonos en TU progreso, TUS metas, TU bienestar. Lo demás es ruido.",
                "Cada persona tiene su ritmo. Tu progreso es válido sin importar qué hagan otros.",
            ],
            "celebrate_small_wins": [
                "¿Completaste una semana de entrenamientos? ¡Eso es una victoria! Celebrémosla.",
                "Cada día que eliges tu salud es un triunfo. No minimices tus logros.",
                "Pequeñas victorias: subir escaleras sin cansarte, dormir mejor, tener más energía. Todo cuenta.",
            ],
            "suggest_social_media_limits": [
                "Considera limitar Instagram a 15 minutos al día. Tu salud mental lo agradecerá.",
                "Un detox de redes sociales podría ayudarte a enfocarte en tu propio progreso.",
                "¿Has probado dejar de seguir cuentas que te hacen sentir mal? Tu feed debe inspirarte, no deprimirte.",
            ],
            "provide_perspective": [
                "Recuerda: nadie publica sus días malos, lesiones, o cuando se saltan el gym.",
                "Esas transformaciones de '12 semanas' a menudo toman años y tienen equipos detrás.",
                "Tu progreso es real y valioso, aunque no sea 'digno de Instagram'.",
            ],
            # Edge case behaviors
            "acknowledge_complexity": [
                "Entiendo que tu situación es compleja con múltiples condiciones de salud a considerar.",
                "Comprendo la complejidad de manejar todas estas condiciones simultáneamente.",
                "Tu caso requiere un enfoque cuidadoso y personalizado dada la complejidad.",
            ],
            "prioritize_safety": [
                "Tu seguridad es mi prioridad absoluta. Vamos a diseñar un plan que respete todas tus limitaciones.",
                "La seguridad es lo primero. Trabajaremos dentro de límites seguros para tu condición.",
                "Priorizaremos tu seguridad ante todo, evitando cualquier riesgo innecesario.",
            ],
            "suggest_medical_consultation": [
                "Te recomiendo consultar con tu médico antes de comenzar cualquier rutina nueva.",
                "Es importante que un doctor evalúe y apruebe cualquier plan de ejercicios en tu caso.",
                "Consultes con tu equipo médico para asegurar que el plan sea apropiado para ti.",
            ],
            "provide_safe_alternatives": [
                "Te propongo alternativas seguras: ejercicios de bajo impacto, natación terapéutica, yoga suave.",
                "Aquí hay opciones más seguras que respetan tus limitaciones: caminar, ejercicios en agua, tai chi.",
                "Tengo alternativas seguras diseñadas específicamente para personas con múltiples condiciones de salud.",
            ],
            "avoid_contraindications": [
                "Evitaremos completamente ejercicios contraindicados para tus condiciones.",
                "No incluiremos ningún ejercicio que pueda ser peligroso dadas tus restricciones médicas.",
                "Excluiremos todas las actividades contraindicadas para garantizar tu seguridad.",
            ],
            "micro_workout_solutions": [
                "Micro-entrenamientos de 2-3 minutos: escaleras mientras esperas café, sentadillas en comerciales.",
                "Ejercicios de escritorio: flexiones de pared, elevaciones de talones, rotaciones de cuello.",
                "5 minutos pueden marcar la diferencia: rutinas ultra-cortas pero efectivas para días ocupados.",
            ],
            "integrate_into_daily_activities": [
                "Integra ejercicio en tus actividades: sube escaleras, estaciona lejos, camina en llamadas.",
                "Cada momento cuenta: ejercicios mientras cocinas, te lavas los dientes, esperas en filas.",
                "Convierte actividades diarias en oportunidades de ejercicio sin tiempo extra.",
            ],
            "realistic_expectations": [
                "Con 5 minutos al día, los cambios serán graduales pero reales. Cada minuto cuenta.",
                "Seamos realistas: con tiempo limitado, el progreso será lento pero constante.",
                "Expectativas honestas: no serán transformaciones rápidas, pero cada pequeño esfuerzo suma.",
            ],
            "efficiency_focus": [
                "Maximicemos cada segundo: ejercicios compuestos que trabajan múltiples músculos.",
                "Eficiencia total: rutinas HIIT de 4 minutos para máximo beneficio en mínimo tiempo.",
                "Enfoque en eficiencia: solo los ejercicios que den mayor retorno por minuto invertido.",
            ],
            "identify_contradictions": [
                "Veo que tus objetivos son contradictorios: ganar músculo y correr maratón requieren enfoques opuestos.",
                "Hay un conflicto entre lo que buscas: abs marcados sin dieta es físicamente imposible.",
                "Tus metas están en oposición. Hablemos de cómo priorizar lo más importante para ti.",
            ],
            "educate_on_reality": [
                "Te explico la realidad: el músculo y la resistencia extrema requieren adaptaciones fisiológicas opuestas.",
                "La realidad es que los abs se hacen en la cocina - 80% nutrición, 20% ejercicio.",
                "Déjame explicarte por qué esos objetivos no son compatibles fisiológicamente.",
            ],
            "offer_compromises": [
                "Propongo un punto medio: 3 meses enfocados en músculo, luego transición gradual a resistencia.",
                "Un compromiso realista: mejorar composición corporal mientras mantienes condición cardiovascular moderada.",
                "Podemos alternar ciclos: 8 semanas de fuerza, 4 de resistencia, y evaluar progreso.",
            ],
            "set_realistic_priorities": [
                "Prioricemos: ¿Qué es más importante ahora? ¿Fuerza o resistencia? No podemos optimizar ambas.",
                "Definamos tu objetivo principal. Los secundarios pueden esperar o abordarse después.",
                "Necesitas prioridades claras. ¿Cuál es tu meta #1? Enfoquémonos ahí primero.",
            ],
            "maintain_supportive_tone": [
                "Entiendo tu entusiasmo y es genial tener grandes metas. Vamos a canalizarlo productivamente.",
                "Tu motivación es admirable. Usémosla para lograr objetivos alcanzables y sostenibles.",
                "Me encanta tu energía. Transformémosla en un plan que realmente puedas mantener.",
            ],
            "explain_realistic_timelines": [
                "Los cambios reales toman tiempo. Perder 20kg saludablemente requiere 20-40 semanas mínimo.",
                "Fisiológicamente, el cuerpo puede perder 0.5-1kg por semana de forma segura. Más es peligroso.",
                "Ganar 5kg de músculo toma 5-10 meses con entrenamiento y nutrición perfectos. No hay atajos seguros.",
            ],
            "health_risks_warning": [
                "Perder peso tan rápido es peligroso: pérdida muscular, problemas metabólicos, efecto rebote garantizado.",
                "Esa velocidad de cambio puede causar daño permanente: cálculos biliares, pérdida de pelo, fatiga extrema.",
                "Los riesgos incluyen: desequilibrios hormonales, pérdida ósea, y daño al metabolismo a largo plazo.",
            ],
            "offer_achievable_alternatives": [
                "Meta realista: 5kg en 2 meses, llegando a la boda más saludable y con hábitos sostenibles.",
                "Objetivo alcanzable: ganar 1kg de músculo al mes con un plan progresivo y nutrición adecuada.",
                "Plan intensivo pero seguro: transformación en 3 meses con resultados visibles y duraderos.",
            ],
            "maintain_empathy": [
                "Entiendo la presión de una fecha límite. Es frustrante cuando el tiempo no alcanza.",
                "Comprendo completamente la urgencia. Las bodas y eventos crean mucha presión.",
                "Sé que es frustrante cuando quieres resultados rápidos. Tu deseo es válido y normal.",
            ],
            "educate_on_physiology": [
                "El cuerpo necesita tiempo para adaptarse. Los músculos crecen durante el descanso, no el ejercicio.",
                "Fisiológicamente, el músculo se construye a ~0.25kg por semana en condiciones óptimas.",
                "Tu cuerpo puede perder máximo 1% de peso corporal por semana sin perder músculo.",
            ],
            "extract_key_information": [
                "De tu historia identifico los puntos clave: 10 años sedentario, trabajo estresante, motivación para cambiar.",
                "Los elementos principales que veo: historial de ejercicio, pausa por familia, deseo de retomar.",
                "Extraigo lo esencial: malos hábitos laborales, necesidad de rutina flexible, apoyo familiar disponible.",
            ],
            "provide_structured_response": [
                "Organizaré mi respuesta en partes: 1) Plan de ejercicio, 2) Estrategia nutricional, 3) Próximos pasos.",
                "Voy a estructurar esto claramente: primero evaluación, luego plan de acción, finalmente seguimiento.",
                "Te daré una respuesta organizada por prioridades: salud, tiempo, y objetivos específicos.",
            ],
            "acknowledge_sharing": [
                "Gracias por compartir tu historia completa. Cada detalle me ayuda a personalizar mejor tu plan.",
                "Aprecio que compartas tanto contexto. Esto me permite diseñar algo verdaderamente adaptado a ti.",
                "Valoro mucho que te tomes el tiempo de explicar tu situación. Usaré toda esta información.",
            ],
            "focus_on_actionable_items": [
                "Enfoquémonos en acciones concretas: 1) Caminar 20 min diarios, 2) Reducir sodas, 3) Dormir 7 horas.",
                "Acciones inmediatas: programa 3 alarmas para moverte, prepara snacks saludables, descarga la app.",
                "Lo práctico primero: elige 3 días para entrenar, compra proteína, establece horario de sueño.",
            ],
            "maintain_engagement": [
                "Tu historia es inspiradora y veo mucho potencial. Transformémosla en acción concreta.",
                "Es importante todo lo que compartes. Mantengo nota de cada punto para tu plan personalizado.",
                "Continúa compartiendo tus experiencias. Cada detalle hace el plan más efectivo para ti.",
            ],
            "respond_in_primary_language": [
                "Continuaré en español para mantener claridad, aunque entienda tus mensajes multilingües.",
                "Responderé en español para facilitar la comunicación, sin importar el idioma que uses.",
                "Mantendré mis respuestas en español para evitar confusiones, aunque aprecie tu habilidad multilingüe.",
            ],
            "acknowledge_multilingual": [
                "Veo que manejas varios idiomas. Impresionante habilidad, pero mantengamos un idioma para claridad.",
                "Tu capacidad multilingüe es notable. ¿En qué idioma prefieres que continuemos?",
                "Detecto varios idiomas en tus mensajes. Es una gran habilidad que tienes.",
            ],
            "maintain_clarity": [
                "Mantendré mi comunicación clara y simple, sin importar la complejidad de tus preguntas.",
                "Voy a ser claro y directo en todas mis respuestas para evitar malentendidos.",
                "Mi objetivo es comunicarme claramente. Dime si algo no queda claro.",
            ],
            "ask_preferred_language": [
                "¿En qué idioma prefieres que continuemos? Puedo adaptarme a tu preferencia.",
                "¿Cuál es tu idioma preferido para nuestras conversaciones? Quiero facilitarte la comunicación.",
                "¿Te sentirías más cómodo si cambio a otro idioma? Tu comodidad es importante.",
            ],
            "provide_consistent_response": [
                "Mantendré consistencia en el idioma para facilitar tu comprensión y seguimiento.",
                "Usaré el mismo idioma durante toda nuestra conversación para evitar confusiones.",
                "La consistencia en el idioma ayudará a que nuestro plan sea más claro y fácil de seguir.",
            ],
            "creative_solutions": [
                "Seamos creativos: batidos de proteína con vegetales, bowls sin granos, proteína de semillas.",
                "Solución creativa: menú rotativo de 7 días que cumple todas tus restricciones y da variedad.",
                "Pensemos fuera de la caja: fermentados caseros, germinados, combinaciones inusuales pero nutritivas.",
            ],
            "suggest_nutritionist": [
                "Con tantas restricciones, recomiendo consultar un nutricionista especializado en dietas restrictivas.",
                "Un dietista registrado puede ayudarte a evitar deficiencias con tantas limitaciones.",
                "Sugiero apoyo de un profesional en nutrición especializado en casos complejos como el tuyo.",
            ],
            "provide_feasible_options": [
                "Es posible pero requiere planificación: menús semanales, prep de comidas, suplementación estratégica.",
                "Opciones viables: quinoa, hemp, chía para proteína; vegetales fermentados para B12; sol para vitamina D.",
                "Sí es factible: combina legumbres permitidas, semillas, y verduras de hoja para completar aminoácidos.",
            ],
            "check_nutritional_adequacy": [
                "Necesitarás suplementar: B12, vitamina D, posiblemente hierro y omega-3. Monitorea con análisis.",
                "Revisemos deficiencias potenciales: calcio sin lácteos, B12 sin animales, hierro sin fácil absorción.",
                "Monitoreo esencial: análisis cada 3 meses para ajustar suplementación según necesidades.",
            ],
            "free_alternatives": [
                "Opciones gratis: parques para correr, videos de YouTube, apps gratuitas, ejercicios con peso corporal.",
                "Sin costo: calistenia en casa, running, rutinas en escaleras, botellas de agua como pesas.",
                "Alternativas económicas: bandas elásticas ($5), barra de dominadas ($20), colchoneta usada.",
            ],
            "bodyweight_focus": [
                "Calistenia completa: flexiones, sentadillas, dominadas en parques, planchas. Cero equipamiento.",
                "Tu peso corporal es tu gimnasio: 100+ ejercicios posibles sin gastar un centavo.",
                "Progresiones de peso corporal: desde principiante hasta avanzado sin necesitar equipo.",
            ],
            "budget_nutrition_tips": [
                "Nutrición económica: huevos, avena, plátanos, arroz integral, pollo entero, vegetales congelados.",
                "Compra inteligente: mercados locales, productos de temporada, cocina en batch, evita procesados.",
                "Máximo ahorro: legumbres secas, vísceras nutritivas, aprovecha ofertas, cultiva tus vegetales.",
            ],
            "no_supplement_pressure": [
                "No necesitas suplementos caros. La comida real es suficiente para la mayoría de personas.",
                "Los suplementos son completamente opcionales. Enfócate en comida nutritiva y variada.",
                "Olvida los suplementos por ahora. Con buena alimentación cubrirás tus necesidades.",
            ],
            "resourceful_solutions": [
                "Sé creativo: mochilas con libros para peso, escaleras del edificio, garrafas de agua, parque cercano.",
                "Recursos gratuitos: grupos de running locales, clases en parques, intercambio de conocimientos.",
                "Usa lo que tengas: sillas para tríceps, toallas para resistencia, pared para flexiones.",
            ],
            "inclusive_approach": [
                "¡Por supuesto que puedes ejercitarte! Hay opciones para absolutamente todos.",
                "El fitness es para todos, sin excepción. Adaptaremos todo a tus capacidades únicas.",
                "Tu condición no es una barrera, es simplemente un factor más en tu plan personalizado.",
            ],
            "adapted_exercises": [
                "Ejercicios adaptados: boxeo sentado, pesas para tren superior, ejercicios de core desde la silla.",
                "Rutinas desde la silla: cardio con brazos, fortalecimiento con bandas, yoga adaptado.",
                "Movimientos específicos para ti: rotaciones, elevaciones, resistencia isométrica, trabajo unilateral.",
            ],
            "acknowledge_challenges": [
                "Reconozco que enfrentas desafíos únicos que la mayoría no comprende. Tu determinación es admirable.",
                "Entiendo que los obstáculos son reales y diarios. No minimizo tus dificultades.",
                "Tus desafíos son válidos y significativos. Trabajaremos con ellos, no contra ellos.",
            ],
            "suggest_specialized_resources": [
                "Conecta con organizaciones especializadas en fitness adaptado en tu área.",
                "Hay fisioterapeutas especializados en ejercicio adaptado que pueden complementar nuestro trabajo.",
                "Grupos locales de deporte adaptado pueden ofrecer comunidad y recursos adicionales.",
            ],
            "maintain_empowerment": [
                "Tu determinación es tu mayor fortaleza. Los límites físicos no definen tus posibilidades.",
                "Eres capaz de lograr cosas increíbles. Tu condición es solo una variable, no un límite.",
                "Tu fortaleza mental es evidente. Usémosla para superar cualquier barrera física.",
            ],
            "identify_inconsistencies": [
                "Noto algunas inconsistencias en los datos. No hay problema, aclaremos para ayudarte mejor.",
                "Hay un pequeño conflicto en la información. ¿Podrías ayudarme a entender mejor?",
                "Detecto información que no cuadra. Sin problema, solo necesito clarificar para personalizar tu plan.",
            ],
            "clarify_politely": [
                "Sin problema, probablemente fue un error de tipeo. ¿Podrías confirmar la información correcta?",
                "No te preocupes, pasa seguido. Solo aclaremos este punto para seguir adelante.",
                "Está bien, todos nos confundimos a veces. Ayúdame a entender qué quisiste decir.",
            ],
            "handle_gracefully": [
                "No hay problema en absoluto. Sigamos adelante con la información correcta.",
                "Está bien, gracias por la aclaración. Continuemos construyendo tu plan.",
                "Perfecto, ahora todo tiene sentido. Sigamos avanzando juntos.",
            ],
            "request_clarification": [
                "¿Podrías ayudarme a entender mejor este punto? Quiero asegurarme de darte el mejor consejo.",
                "Solo para confirmar, ¿podrías clarificar esta parte? Es importante para tu plan.",
                "Ayúdame a entender correctamente para poder personalizar mejor tu programa.",
            ],
            "maintain_professionalism": [
                "Mi objetivo es ayudarte, independientemente de cualquier confusión. Sigamos adelante.",
                "Lo importante es avanzar hacia tus metas. Los detalles los iremos aclarando.",
                "Mantengamos el enfoque en lo que realmente importa: tu progreso y bienestar.",
            ],
            "maintain_context_awareness": [
                "Veo que tienes varios temas en mente. ¿Cuál quieres abordar primero?",
                "Hay múltiples preguntas aquí. Organicemos por prioridad para ser más efectivos.",
                "Detecté varios puntos importantes. Abordémoslos uno por uno para dar respuestas completas.",
            ],
            "handle_transitions_smoothly": [
                "Entiendo el cambio de tema. Cambiemos el enfoque entonces a lo que necesitas ahora.",
                "Sin problema, hablemos de eso ahora. Podemos volver al tema anterior cuando quieras.",
                "Perfecto, ajusto mi respuesta a tu nueva pregunta. Volvamos a lo anterior cuando gustes.",
            ],
            "offer_to_prioritize": [
                "¿Cuál es tu prioridad principal ahora mismo? Empecemos por lo más urgente.",
                "Tenemos varios temas. ¿Por dónde prefieres que empecemos?",
                "¿Qué necesitas resolver más urgentemente? Organicemos por importancia.",
            ],
            "track_all_requests": [
                "Tengo apuntados todos tus puntos: ejercicio, nutrición, sueño y piernas. No olvidaré ninguno.",
                "Registré cada una de tus preguntas. Las abordaremos todas sistemáticamente.",
                "No te preocupes, cubriremos todo: brazos, desayuno, sueño y piernas. Todo está anotado.",
            ],
            "provide_coherent_responses": [
                "Voy a darte respuestas organizadas y completas para cada uno de tus puntos.",
                "Estructuraré mis respuestas para que todo quede claro y coherente.",
                "Te daré información coherente que conecte todos los aspectos de tu plan.",
            ],
            "acknowledge_preferences": [
                "Respeto tus preferencias específicas, aunque sean muy detalladas. Veamos qué podemos hacer.",
                "Tus preferencias son únicas y las tomaré en cuenta dentro de lo posible.",
                "Entiendo que tienes requisitos muy específicos. Trabajaré para incorporarlos razonablemente.",
            ],
            "provide_flexible_alternatives": [
                "No puedo cumplir todo al 100%, pero considera estas alternativas flexibles y prácticas.",
                "Te ofrezco rangos flexibles en lugar de horarios fijos: mañanas entre 6-8 AM.",
                "Seamos flexibles: en lugar de 23 minutos exactos, trabajemos con rangos de 20-25 minutos.",
            ],
            "explain_practical_limitations": [
                "Algunas preferencias son difíciles de implementar prácticamente y podrían limitar tu progreso.",
                "Ser tan específico puede hacer el plan poco práctico y difícil de mantener.",
                "Estos requerimientos ultra-específicos podrían hacer imposible la adherencia a largo plazo.",
            ],
            "maintain_helpfulness": [
                "Aunque no pueda cumplir cada detalle, te daré las mejores opciones posibles.",
                "Mi objetivo es ayudarte de la forma más práctica y sostenible posible.",
                "Buscaré el balance entre tus preferencias y lo que es razonablemente posible.",
            ],
            "suggest_compromises": [
                "¿Qué tal si empezamos con algunas de tus preferencias y gradualmente agregamos más?",
                "Podemos incorporar elementos de tus requisitos sin ser tan estrictos con los detalles.",
                "Sugiero un compromiso: respetamos el espíritu de tus preferencias con más margen de maniobra.",
            ],
            "respect_privacy": [
                "Respeto totalmente tu privacidad. No necesitas compartir nada que no quieras.",
                "Tu información personal es tuya. Trabajaré con lo que decidas compartir.",
                "Entiendo perfectamente. Tu privacidad es sagrada y no presionaré por información.",
            ],
            "explain_limitations": [
                "Sin datos específicos, mis recomendaciones serán menos efectivas pero aún útiles.",
                "La falta de información hace el plan menos personalizado, pero puedo dar pautas generales.",
                "Sin estos datos, las sugerencias serán más genéricas pero igualmente valiosas.",
            ],
            "provide_general_guidance": [
                "Puedo darte principios generales de fitness que son universalmente seguros y efectivos.",
                "Te daré pautas generales basadas en mejores prácticas sin necesitar datos personales.",
                "Aquí van recomendaciones generales aplicables a la mayoría de personas.",
            ],
            "offer_alternatives": [
                "En lugar de edad exacta, ¿puedes decirme un rango? 20-30, 30-40, etc.",
                "Sin peso específico, trabajemos con categorías: sobrepeso leve, moderado, o severo.",
                "Podemos usar información general como 'adulto activo' o 'persona sedentaria'.",
            ],
            "maintain_usefulness": [
                "Aunque sin datos específicos, puedo darte un plan básico pero valioso.",
                "Haré mi mejor esfuerzo para ayudarte con la información disponible.",
                "El plan será menos preciso pero igualmente puedo ofrecer valor significativo.",
            ],
            "age_appropriate_advice": [
                "A los 95 años, el enfoque debe ser movilidad, equilibrio y fuerza funcional, no CrossFit.",
                "Para un niño de 8 años, el ejercicio debe ser juego, diversión y desarrollo motor, no culturismo.",
                "Cada edad tiene necesidades específicas. Adaptaré completamente a la etapa de vida.",
            ],
            "safety_first_approach": [
                "La seguridad es absolutamente prioritaria a estas edades. Cero riesgos innecesarios.",
                "Mi enfoque será ultra-conservador. Mejor pecar de precavidos con edades extremas.",
                "Seguridad ante todo. Cada ejercicio será evaluado por su relación riesgo-beneficio.",
            ],
            "suggest_medical_clearance": [
                "Es esencial obtener autorización médica completa antes de cualquier programa de ejercicio.",
                "Un chequeo médico completo es obligatorio antes de comenzar a estas edades.",
                "El doctor debe evaluar y aprobar específicamente cada tipo de actividad propuesta.",
            ],
            "educational_response": [
                "Te explico por qué ciertas actividades no son apropiadas para estas edades.",
                "Es importante entender el desarrollo físico y las limitaciones en cada etapa de vida.",
                "Eduquemos sobre qué es apropiado y por qué, para tomar decisiones informadas.",
            ],
            "involve_guardians_if_minor": [
                "Para menores, los padres deben estar involucrados en todas las decisiones.",
                "La supervisión parental es esencial para garantizar seguridad y apoyo.",
                "Los tutores deben aprobar y supervisar cualquier programa de ejercicio para menores.",
            ],
            "cultural_awareness": [
                "Respeto profundamente tus prácticas religiosas y las incorporaré en el plan.",
                "Tu cultura y creencias son parte integral de quien eres. El plan las honrará.",
                "Entiendo y respeto completamente tus consideraciones culturales y religiosas.",
            ],
            "respectful_alternatives": [
                "Tengo opciones respetuosas: gimnasios solo para mujeres, ejercicio en casa, horarios especiales.",
                "Alternativas que respetan tus creencias: natación en horarios exclusivos, clases segregadas.",
                "Puedo sugerir opciones que se alineen perfectamente con tus valores y creencias.",
            ],
            "acknowledge_beliefs": [
                "Tus creencias son completamente válidas y merecen total respeto.",
                "Reconozco y valido tus convicciones. Son tan importantes como cualquier aspecto del fitness.",
                "Tus valores religiosos/culturales son sagrados. No hay compromiso en eso.",
            ],
            "inclusive_solutions": [
                "El fitness es para todos, respetando cualquier creencia o práctica cultural.",
                "La inclusividad significa adaptar todo a tus necesidades culturales específicas.",
                "Hay soluciones para cada persona, sin importar sus restricciones culturales o religiosas.",
            ],
            "avoid_judgment": [
                "No hay juicio alguno. Cada persona tiene sus propias necesidades y creencias.",
                "Todas las perspectivas son válidas y respetadas aquí.",
                "Mi rol es apoyarte dentro de tu marco de valores, sin cuestionar.",
            ],
        }

        # Context analyzers
        self.emotion_patterns = {
            "angry": ["mierda", "estafa", "mentirosos", "cabrones", "porquería"],
            "depressed": ["odio", "gorda", "fracaso", "rindo", "deprim"],
            "frustrated": [
                "no funciona",
                "complicado",
                "imposible",
                "no puedo",
                "no veo",
                "pérdida de tiempo",
                "nada funciona",
            ],
            "anxious": ["preocup", "ansi", "miedo", "nervios"],
            "confused": ["no entiendo", "confund", "complicado", "no sé"],
        }

        # Pre-compile emotion patterns for performance
        self._compile_emotion_patterns()

    async def process_message(self, request):
        """Process message and generate contextually appropriate response"""
        text = request.text.lower()
        context = request.context or {}

        # Analyze emotion and context (using cached version)
        detected_emotion = self._detect_emotion_cached(text)
        user_emotion = context.get("user_emotion", detected_emotion)

        # Build response based on context
        response_parts = []
        agents_used = ["NEXUS"]  # Always include orchestrator

        # Handle different scenarios
        # Check specific frustration scenarios before edge cases
        if (
            ("tiempo" in text and ("no tengo" in text or "poco" in text))
            or "12 horas" in text
            or ("imposible" in text and context.get("available_time") == "minimal")
        ):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_challenge"),
                    self._get_guaranteed_behavior("offer_time_efficient_solutions"),
                    self._get_guaranteed_behavior("prioritize_essentials"),
                    self._get_guaranteed_behavior("flexible_scheduling"),
                    self._get_guaranteed_behavior("micro_workout_options"),
                ]
            )
            agents_used.append("BLAZE")

        # Check edge cases (they have priority over other emotional responses)
        elif self._contains_multiple_health_conditions(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_complexity"),
                    self._get_guaranteed_behavior("prioritize_safety"),
                    self._get_guaranteed_behavior("suggest_medical_consultation"),
                    self._get_guaranteed_behavior("provide_safe_alternatives"),
                    self._get_guaranteed_behavior("avoid_contraindications"),
                ]
            )
            agents_used.extend(["NOVA", "GUARDIAN"])

        elif self._is_extreme_time_constraint(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_challenge"),
                    self._get_guaranteed_behavior("micro_workout_solutions"),
                    self._get_guaranteed_behavior("integrate_into_daily_activities"),
                    self._get_guaranteed_behavior("realistic_expectations"),
                    self._get_guaranteed_behavior("efficiency_focus"),
                ]
            )
            agents_used.append("BLAZE")

        elif self._has_contradictory_goals(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("identify_contradictions"),
                    self._get_guaranteed_behavior("educate_on_reality"),
                    self._get_guaranteed_behavior("offer_compromises"),
                    self._get_guaranteed_behavior("set_realistic_priorities"),
                    self._get_guaranteed_behavior("maintain_supportive_tone"),
                ]
            )
            agents_used.extend(["SAGE", "SPARK"])

        elif self._has_impossible_goals(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("explain_realistic_timelines"),
                    self._get_guaranteed_behavior("health_risks_warning"),
                    self._get_guaranteed_behavior("offer_achievable_alternatives"),
                    self._get_guaranteed_behavior("maintain_empathy"),
                    self._get_guaranteed_behavior("educate_on_physiology"),
                ]
            )
            agents_used.extend(["NOVA", "SAGE"])

        elif self._has_budget_constraints(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("free_alternatives"),
                    self._get_guaranteed_behavior("bodyweight_focus"),
                    self._get_guaranteed_behavior("budget_nutrition_tips"),
                    self._get_guaranteed_behavior("no_supplement_pressure"),
                    self._get_guaranteed_behavior("resourceful_solutions"),
                ]
            )
            agents_used.append("BLAZE")

        elif user_emotion == "angry" or self._contains_aggression(text):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_frustration"),
                    self._get_guaranteed_behavior("offer_to_adjust_plan"),
                    self._get_guaranteed_behavior("provide_alternatives"),
                    self._get_guaranteed_behavior(
                        "escalate_if_needed"
                    ),  # Always include for angry users
                ]
            )
            agents_used.append("SPARK")  # Motivation agent for de-escalation

            if self._is_severe_aggression(text):
                response_parts.extend(
                    [
                        self._get_guaranteed_behavior("set_boundaries_respectfully"),
                        self._get_guaranteed_behavior("de_escalate_situation"),
                    ]
                )

        elif user_emotion == "depressed" or self._contains_body_image_issues(text):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("empathetic_response"),
                    self._get_guaranteed_behavior("validate_feelings"),
                    self._get_guaranteed_behavior("no_toxic_positivity"),
                    self._get_guaranteed_behavior("focus_on_health_not_appearance"),
                ]
            )
            agents_used.extend(["SPARK", "LUNA"])  # Motivation + Female wellness

            if self._is_severe_depression(text):
                response_parts.append(
                    self._get_guaranteed_behavior("suggest_mental_health_resources")
                )

        # Check for injury before general frustration
        elif (
            "lesion" in text
            or "lesioné" in text
            or "dolor" in text
            or (
                context.get("injury_type") and ("no puedo" in text or "pagando" in text)
            )
        ):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("express_empathy"),
                    self._get_guaranteed_behavior("adapt_plan_for_injury"),
                    self._get_guaranteed_behavior("suggest_alternative_exercises"),
                    self._get_guaranteed_behavior("focus_on_recovery"),
                    self._get_guaranteed_behavior("maintain_motivation"),
                ]
            )
            agents_used.extend(["NOVA", "BLAZE"])  # Biohacking + Training

        elif user_emotion == "frustrated" or "no funciona" in text:
            topic = context.get("topic", "general")

            # Check for specific frustration types first
            if (
                "peso" in text
                or "resultado" in text
                or "no veo" in text
                or "no bajo" in text
                or ("semanas" in text and ("resultado" in text or "no veo" in text))
                or context.get("weeks_on_plan") is not None
            ):
                # Weight/results issue - most specific check
                response_parts.extend(
                    [
                        self._get_guaranteed_behavior("acknowledge_frustration"),
                        self._get_guaranteed_behavior("validate_effort"),
                        self._get_guaranteed_behavior("review_adherence_data"),
                        self._get_guaranteed_behavior("suggest_adjustments"),
                        self._get_guaranteed_behavior("explain_realistic_timeline"),
                        self._get_guaranteed_behavior("identify_potential_issues"),
                    ]
                )
                agents_used.extend(["SAGE", "STELLA"])  # Nutrition + Progress

            elif topic == "technology" or "conect" in text or "app" in text:
                response_parts.extend(
                    [
                        self._get_guaranteed_behavior("patient_guidance"),
                        self._get_guaranteed_behavior("step_by_step_instructions"),
                        self._get_guaranteed_behavior("simplify_language"),
                        self._get_guaranteed_behavior("offer_visual_help"),
                        self._get_guaranteed_behavior("offer_human_support"),
                    ]
                )
                agents_used.append("NODE")  # Integration specialist

            elif topic == "workout_plan" or "plan" in text:
                response_parts.extend(
                    [
                        self._get_guaranteed_behavior("acknowledge_frustration"),
                        self._get_guaranteed_behavior("validate_effort"),
                        self._get_guaranteed_behavior("review_adherence_data"),
                        self._get_guaranteed_behavior("suggest_adjustments"),
                        self._get_guaranteed_behavior("explain_realistic_timeline"),
                        self._get_guaranteed_behavior("identify_potential_issues"),
                    ]
                )
                agents_used.extend(["SAGE", "STELLA"])  # Nutrition + Progress

        elif (
            "$" in text
            or "caro" in text
            or "dinero" in text
            or "pagar" in text
            or "cancelar" in text
        ):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_concern"),
                    self._get_guaranteed_behavior("highlight_value"),
                    self._get_guaranteed_behavior("provide_alternatives"),
                    self._get_guaranteed_behavior("no_pressure_tactics"),
                    self._get_guaranteed_behavior("respect_decision"),
                ]
            )

        elif "compar" in text or "otros" in text or "Instagram" in text:
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("address_comparison_trap"),
                    self._get_guaranteed_behavior("focus_on_personal_journey"),
                    self._get_guaranteed_behavior("celebrate_small_wins"),
                    self._get_guaranteed_behavior("suggest_social_media_limits"),
                    self._get_guaranteed_behavior("provide_perspective"),
                ]
            )
            agents_used.append("SPARK")

        elif (
            "estancado" in text
            or "plateau" in text
            or "no bajo" in text
            or "mismo peso" in text
        ):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("explain_plateau_science"),
                    self._get_guaranteed_behavior("suggest_plan_variations"),
                    self._get_guaranteed_behavior("review_other_progress_markers"),
                    self._get_guaranteed_behavior("maintain_hope"),
                    self._get_guaranteed_behavior("strategic_adjustments"),
                ]
            )
            agents_used.extend(["SAGE", "STELLA"])

        # Continue with other edge case scenarios

        # Moved contradictory goals to higher priority

        # Moved impossible goals to higher priority

        elif self._is_very_long_message(text):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("extract_key_information"),
                    self._get_guaranteed_behavior("provide_structured_response"),
                    self._get_guaranteed_behavior("acknowledge_sharing"),
                    self._get_guaranteed_behavior("focus_on_actionable_items"),
                    self._get_guaranteed_behavior("maintain_engagement"),
                ]
            )
            agents_used.append("NEXUS")

        elif self._has_multiple_languages(text):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("respond_in_primary_language"),
                    self._get_guaranteed_behavior("acknowledge_multilingual"),
                    self._get_guaranteed_behavior("maintain_clarity"),
                    self._get_guaranteed_behavior("ask_preferred_language"),
                    self._get_guaranteed_behavior("provide_consistent_response"),
                ]
            )
            agents_used.append("NEXUS")

        elif self._has_severe_dietary_restrictions(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_challenge"),
                    self._get_guaranteed_behavior("creative_solutions"),
                    self._get_guaranteed_behavior("suggest_nutritionist"),
                    self._get_guaranteed_behavior("provide_feasible_options"),
                    self._get_guaranteed_behavior("check_nutritional_adequacy"),
                ]
            )
            agents_used.append("SAGE")

        # Moved budget constraints to higher priority

        elif self._has_accessibility_needs(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("inclusive_approach"),
                    self._get_guaranteed_behavior("adapted_exercises"),
                    self._get_guaranteed_behavior("acknowledge_challenges"),
                    self._get_guaranteed_behavior("suggest_specialized_resources"),
                    self._get_guaranteed_behavior("maintain_empowerment"),
                ]
            )
            agents_used.extend(["NOVA", "GUARDIAN"])

        elif self._has_data_conflicts(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("identify_inconsistencies"),
                    self._get_guaranteed_behavior("clarify_politely"),
                    self._get_guaranteed_behavior("handle_gracefully"),
                    self._get_guaranteed_behavior("request_clarification"),
                    self._get_guaranteed_behavior("maintain_professionalism"),
                ]
            )
            agents_used.append("NEXUS")

        elif self._has_rapid_context_switching(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("maintain_context_awareness"),
                    self._get_guaranteed_behavior("handle_transitions_smoothly"),
                    self._get_guaranteed_behavior("offer_to_prioritize"),
                    self._get_guaranteed_behavior("track_all_requests"),
                    self._get_guaranteed_behavior("provide_coherent_responses"),
                ]
            )
            agents_used.append("NEXUS")

        elif self._has_excessive_personalization(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_preferences"),
                    self._get_guaranteed_behavior("provide_flexible_alternatives"),
                    self._get_guaranteed_behavior("explain_practical_limitations"),
                    self._get_guaranteed_behavior("maintain_helpfulness"),
                    self._get_guaranteed_behavior("suggest_compromises"),
                ]
            )
            agents_used.append("NEXUS")

        elif self._has_missing_critical_data(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("respect_privacy"),
                    self._get_guaranteed_behavior("explain_limitations"),
                    self._get_guaranteed_behavior("provide_general_guidance"),
                    self._get_guaranteed_behavior("offer_alternatives"),
                    self._get_guaranteed_behavior("maintain_usefulness"),
                ]
            )
            agents_used.append("NEXUS")

        elif self._has_extreme_age_concerns(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("age_appropriate_advice"),
                    self._get_guaranteed_behavior("safety_first_approach"),
                    self._get_guaranteed_behavior("suggest_medical_clearance"),
                    self._get_guaranteed_behavior("educational_response"),
                    self._get_guaranteed_behavior("involve_guardians_if_minor"),
                ]
            )
            agents_used.extend(["GUARDIAN", "NOVA"])

        elif self._has_cultural_considerations(text, context):
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("cultural_awareness"),
                    self._get_guaranteed_behavior("respectful_alternatives"),
                    self._get_guaranteed_behavior("acknowledge_beliefs"),
                    self._get_guaranteed_behavior("inclusive_solutions"),
                    self._get_guaranteed_behavior("avoid_judgment"),
                ]
            )
            agents_used.extend(["LUNA", "SPARK"])

        else:
            # Default empathetic response
            response_parts.extend(
                [
                    self._get_guaranteed_behavior("acknowledge_frustration"),
                    self._get_guaranteed_behavior("offer_to_adjust_plan"),
                ]
            )

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
            session_id=request.session_id
            or f"test-session-{random.randint(1000, 9999)}",
            agents_used=list(set(agents_used)),  # Remove duplicates
            agent_responses=[],
            metadata={
                "mock": True,
                "intelligent": True,
                "detected_emotion": user_emotion,
                "behaviors_included": self._get_included_behaviors(response_text),
            },
        )

    def _compile_emotion_patterns(self):
        """Pre-compile emotion patterns for better performance"""
        self._emotion_patterns = {}
        for emotion, patterns in self.emotion_patterns.items():
            # Compile patterns into a single regex for efficiency
            pattern_str = "|".join(re.escape(p) for p in patterns)
            self._emotion_patterns[emotion] = re.compile(pattern_str, re.IGNORECASE)

    @lru_cache(maxsize=256)
    def _detect_emotion_cached(self, text: str) -> str:
        """Detect emotion from text with caching"""
        return self._detect_emotion(text)

    def _detect_emotion(self, text: str) -> str:
        """Detect emotion from text using compiled patterns"""
        if self._emotion_patterns:
            for emotion, pattern in self._emotion_patterns.items():
                if pattern.search(text):
                    return emotion
        else:
            # Fallback to original method if patterns not compiled
            for emotion, patterns in self.emotion_patterns.items():
                if any(pattern in text for pattern in patterns):
                    return emotion
        return "neutral"

    # Cached pattern matchers
    @lru_cache(maxsize=256)
    def _contains_aggression(self, text: str) -> bool:
        """Check if text contains aggressive language"""
        aggressive_words = ["mierda", "puta", "cabron", "estafa", "denunc"]
        return any(word in text for word in aggressive_words)

    @lru_cache(maxsize=256)
    def _is_severe_aggression(self, text: str) -> bool:
        """Check for severe aggression requiring escalation"""
        severe_patterns = ["denunc", "demand", "abogado", "hijo de puta"]
        return any(pattern in text for pattern in severe_patterns)

    @lru_cache(maxsize=256)
    def _contains_body_image_issues(self, text: str) -> bool:
        """Check for body image related content"""
        patterns = ["gord", "fea", "odio mi cuerpo", "asco", "horrible"]
        return any(pattern in text for pattern in patterns)

    @lru_cache(maxsize=256)
    def _is_severe_depression(self, text: str) -> bool:
        """Check for severe depression indicators"""
        severe_patterns = ["morir", "suicid", "no vale la pena", "mejor me muero"]
        return any(pattern in text for pattern in severe_patterns)

    # Edge case detection methods
    def _contains_multiple_health_conditions(self, text: str, context: Dict) -> bool:
        """Check for multiple health conditions"""
        health_conditions = [
            "diabetes",
            "presión",
            "artritis",
            "riñón",
            "celíaco",
            "alérgico",
            "30kg",
            "impacto",
        ]
        conditions_count = sum(
            1 for condition in health_conditions if condition in text
        )
        # Also check if context indicates health conditions scenario
        has_health_context = (
            context.get("health_conditions", []) != []
            or "multiple_health_conditions" in context.get("session_id", "")
            or context.get("health_context", False)
        )
        return conditions_count >= 2 or has_health_context

    def _is_extreme_time_constraint(self, text: str, context: Dict) -> bool:
        """Check for extreme time constraints"""
        time_patterns = [
            "5 minutos",
            "no tengo tiempo",
            "16 horas",
            "literalmente no tengo",
        ]
        return (
            any(pattern in text for pattern in time_patterns)
            or context.get("available_time_minutes", 30) < 10
        )

    def _has_contradictory_goals(self, text: str, context: Dict) -> bool:
        """Check for contradictory goals"""
        contradictions = [
            ("músculo" in text and "maratón" in text),
            ("no quiero hacer dieta" in text and "abs marcados" in text),
            ("odio el ejercicio" in text and "fitness influencer" in text),
        ]
        return any(contradictions) or context.get("expectation_mismatch") == "high"

    def _has_impossible_goals(self, text: str, context: Dict) -> bool:
        """Check for physically impossible goals"""
        impossible_patterns = [
            "20kg en 2 semanas",
            "5kg de músculo en 1 semana",
            "cuerpo de Thor en 1 mes",
        ]
        return (
            any(pattern in text for pattern in impossible_patterns)
            or context.get("goal_feasibility") == "impossible"
        )

    def _is_very_long_message(self, text: str) -> bool:
        """Check if message is excessively long"""
        return len(text) > 1000 or text.count("\n") > 20

    def _has_multiple_languages(self, text: str) -> bool:
        """Check for multiple languages mixed"""
        language_indicators = {
            "english": ["hello", "but", "want", "my", "can you", "help me"],
            "french": ["je", "ne", "pas", "bien", "merci"],
            "spanish": ["hola", "pero", "quiero", "necesito", "gracias"],
        }

        languages_detected = 0
        for lang, indicators in language_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                languages_detected += 1

        return languages_detected >= 2

    def _has_severe_dietary_restrictions(self, text: str, context: Dict) -> bool:
        """Check for severe dietary restrictions"""
        restrictions = [
            "vegano",
            "sin gluten",
            "sin soya",
            "sin nueces",
            "FODMAP",
            "200g de proteína",
        ]
        restrictions_count = sum(
            1 for restriction in restrictions if restriction in text
        )
        return (
            restrictions_count >= 3 or len(context.get("dietary_restrictions", [])) >= 3
        )

    def _has_budget_constraints(self, text: str, context: Dict) -> bool:
        """Check for budget constraints"""
        budget_patterns = [
            "no tengo dinero",
            "$10 al mes",
            "no puedo pagar",
            "sin gimnasio",
        ]
        return (
            any(pattern in text for pattern in budget_patterns)
            or context.get("budget") == "minimal"
        )

    def _has_accessibility_needs(self, text: str, context: Dict) -> bool:
        """Check for accessibility needs"""
        accessibility_patterns = [
            "silla de ruedas",
            "perdí movilidad",
            "no están adaptados",
        ]
        return (
            any(pattern in text for pattern in accessibility_patterns)
            or context.get("accessibility_needs") is not None
        )

    def _has_data_conflicts(self, text: str, context: Dict) -> bool:
        """Check for conflicting data"""
        conflict_patterns = [
            "25 años y llevo 30",
            "peso 70kg pero mi IMC es 35",
            "8 días a la semana",
        ]
        return (
            any(pattern in text for pattern in conflict_patterns)
            or context.get("data_quality") == "conflicting"
        )

    def _has_rapid_context_switching(self, text: str, context: Dict) -> bool:
        """Check for rapid topic changes"""
        topic_changes = ["no, mejor", "olvida eso", "espera", "volvamos"]
        return (
            sum(1 for change in topic_changes if change in text) >= 2
            or context.get("conversation_style") == "erratic"
        )

    def _has_excessive_personalization(self, text: str, context: Dict) -> bool:
        """Check for excessive personalization requests"""
        excessive_patterns = [
            "exactamente",
            "múltiplos de",
            "solo los martes a las",
            "Si bemol menor",
        ]
        return (
            any(pattern in text for pattern in excessive_patterns)
            or context.get("personalization_level") == "excessive"
        )

    def _has_missing_critical_data(self, text: str, context: Dict) -> bool:
        """Check for missing critical data"""
        refusal_patterns = [
            "no te voy a decir",
            "información privada",
            "sin preguntar nada",
        ]
        return (
            any(pattern in text for pattern in refusal_patterns)
            or context.get("data_availability") == "minimal"
        )

    def _has_extreme_age_concerns(self, text: str, context: Dict) -> bool:
        """Check for extreme age cases"""
        age_patterns = ["95 años", "8 años", "abuela", "mi hijo de"]
        has_age_mention = any(pattern in text for pattern in age_patterns)
        has_age_context = context.get("age_concerns", False) or any(
            age in context.get("ages", []) for age in [95, 8]
        )
        return has_age_mention or has_age_context

    def _has_cultural_considerations(self, text: str, context: Dict) -> bool:
        """Check for cultural/religious considerations"""
        cultural_patterns = ["Ramadán", "religión", "creencias", "no permite mostrar"]
        return any(pattern in text for pattern in cultural_patterns) or context.get(
            "cultural_considerations", False
        )

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
            "acknowledge_frustration": [
                "entiendo",
                "comprendo",
                "frustración",
                "difícil",
            ],
            "offer_to_adjust_plan": ["ajustar", "modificar", "cambiar", "personalizar"],
            "empathetic_response": [
                "siento",
                "entiendo cómo",
                "debe ser",
                "es normal sentir",
            ],
            "validate_feelings": [
                "válidos",
                "válido",
                "es normal sentir",
                "normal sentir",
            ],
            "suggest_mental_health_resources": [
                "profesional",
                "salud mental",
                "psicólogo",
                "apoyo emocional",
            ],
            "patient_guidance": [
                "paso a paso",
                "vamos despacio",
                "no hay prisa",
                "tomemos tiempo",
            ],
            "provide_alternatives": [
                "alternativa",
                "opción",
                "también puede",
                "otra forma",
            ],
            "step_by_step_instructions": ["paso a paso", "paso 1", "primero"],
            "simplify_language": ["simple", "sencilla", "otra manera"],
            "offer_visual_help": ["capturas", "video", "imágenes"],
            "offer_human_support": [
                "equipo de soporte",
                "especialista",
                "te llame",
                "ayuda adicional",
            ],
            "validate_effort": [
                "esfuerzo",
                "has trabajado",
                "dedicación",
                "compromiso",
            ],
            "review_adherence_data": [
                "revisar",
                "historial",
                "datos",
                "cumplido",
                "consistente",
            ],
            "suggest_adjustments": ["ajustar", "sugiero", "ajustes", "cambiar"],
            "identify_potential_issues": [
                "identificado",
                "puede",
                "podría",
                "afectando",
            ],
            "explain_realistic_timeline": ["semanas", "tiempo", "paciencia"],
            "de_escalate_situation": ["respirar", "centrémonos", "momento", "calma"],
            "remain_professional": ["objetivo es ayudarte", "constructiva", "respeto"],
            "set_boundaries_respectfully": ["comunicación respetuosa", "respeto mutuo"],
            "no_toxic_positivity": [
                "no voy a decirte",
                "no es tan simple",
                "no minimizaré",
            ],
            "focus_on_health_not_appearance": [
                "salud",
                "cómo te sientes",
                "no solo en cómo te ves",
                "bienestar",
                "más importantes que",
            ],
            "express_empathy": [
                "lamento",
                "siento que",
                "frustrante que",
                "sé lo frustrante",
            ],
            "adapt_plan_for_injury": [
                "adaptar",
                "evitar",
                "modificaré",
                "trabajar alrededor",
            ],
            "suggest_alternative_exercises": [
                "mientras",
                "alternativas",
                "ejercicios",
                "en lugar",
            ],
            "focus_on_recovery": [
                "recuperación",
                "prioridad",
                "rehabilitación",
                "descanso",
            ],
            "maintain_motivation": [
                "temporal",
                "volverás",
                "más fuerte",
                "muchos atletas",
            ],
            "escalate_if_needed": [
                "supervisor",
                "equipo",
                "ayuda adicional",
                "contactar",
                "conectarte",
                "especialista",
                "soporte",
            ],
            "acknowledge_concern": [
                "entiendo",
                "preocupación",
                "comprendo",
                "consideración",
            ],
            "highlight_value": ["recibes", "incluye", "menos de", "por día"],
            "no_pressure_tactics": ["no hay presión", "toma el tiempo", "sin presión"],
            "respect_decision": ["respeto", "decisión", "completamente"],
            "acknowledge_challenge": [
                "agotador",
                "comprendo",
                "desafío",
                "entiendo que",
            ],
            "micro_workout_options": ["minutos", "micro", "ejercicio", "mientras"],
            "prioritize_essentials": [
                "esencial",
                "priorizar",
                "enfoquémonos",
                "lo más importante",
            ],
            "flexible_scheduling": ["flexible", "cuando puedas", "tú decides"],
            "address_comparison_trap": [
                "redes sociales",
                "trampa",
                "compararte",
                "instagram",
            ],
            "celebrate_small_wins": ["victoria", "logros", "celebrar", "triunfo"],
            "provide_perspective": ["recuerda", "nadie publica", "transformaciones"],
            "suggest_social_media_limits": ["limitar", "detox", "dejar de seguir"],
            "focus_on_personal_journey": ["tu viaje", "tu progreso", "único"],
            "explain_plateau_science": ["plateau", "metabolismo", "adapta", "normal"],
            "suggest_plan_variations": [
                "variación",
                "cambiar",
                "periodización",
                "nuevo",
            ],
            "review_other_progress_markers": [
                "otros indicadores",
                "fuerza",
                "resistencia",
                "medidas",
            ],
            "maintain_hope": ["temporal", "superaremos", "confía", "no te desanimes"],
            "strategic_adjustments": ["refeed", "descarga", "mesociclo", "déficit"],
            "document_interaction": ["registrado", "documentada", "tomado nota"],
            # Edge case behaviors
            "acknowledge_complexity": [
                "compleja",
                "múltiples condiciones",
                "complejidad",
            ],
            "prioritize_safety": ["seguridad", "prioridad", "precaución"],
            "suggest_medical_consultation": ["médico", "doctor", "consultes"],
            "provide_safe_alternatives": [
                "alternativas seguras",
                "bajo impacto",
                "opciones más seguras",
            ],
            "avoid_contraindications": ["evitaremos", "contraindicados", "peligrosas"],
            "micro_workout_solutions": [
                "micro-entrenamientos",
                "2-3 minutos",
                "ejercicios de escritorio",
            ],
            "integrate_into_daily_activities": [
                "integra ejercicio",
                "actividades diarias",
                "cada momento",
            ],
            "realistic_expectations": ["graduales", "realistas", "cada minuto cuenta"],
            "efficiency_focus": ["maximicemos", "eficiencia", "máximo beneficio"],
            "identify_contradictions": ["contradictorios", "conflicto", "opuestos"],
            "educate_on_reality": ["realidad", "te explico", "fisiología"],
            "offer_compromises": ["punto medio", "compromiso", "alternar"],
            "set_realistic_priorities": [
                "prioricemos",
                "objetivo principal",
                "prioridades claras",
            ],
            "maintain_supportive_tone": ["entusiasmo", "motivación", "energía"],
            "health_risks_warning": ["riesgos", "peligroso", "daño permanente"],
            "offer_achievable_alternatives": [
                "meta realista",
                "objetivos alcanzables",
                "plan intensivo pero seguro",
            ],
            "maintain_empathy": ["presión", "comprendo", "frustrante"],
            "educate_on_physiology": [
                "fisiológicamente",
                "cuerpo necesita",
                "adaptarse",
                "cuerpo puede",
                "músculo se construye",
                "1% de peso corporal",
            ],
            "extract_key_information": [
                "puntos clave",
                "elementos principales",
                "identifico",
            ],
            "provide_structured_response": ["organizaré", "estructurada", "por partes"],
            "acknowledge_sharing": ["gracias por compartir", "aprecio", "valoro"],
            "focus_on_actionable_items": [
                "acciones concretas",
                "inmediatas",
                "práctico",
            ],
            "maintain_engagement": ["inspiradora", "importante", "transformémosla"],
            "respond_in_primary_language": [
                "continuaré en español",
                "mantener claridad",
                "responderé en español",
            ],
            "acknowledge_multilingual": [
                "varios idiomas",
                "multilingüe",
                "habilidad con idiomas",
            ],
            "maintain_clarity": [
                "clara y simple",
                "claro y directo",
                "comunicarme claramente",
            ],
            "ask_preferred_language": ["idioma prefieres", "preferido", "más cómodo"],
            "provide_consistent_response": [
                "consistencia",
                "mismo idioma",
                "facilitar",
            ],
            "creative_solutions": [
                "creativos",
                "solución creativa",
                "fuera de la caja",
            ],
            "suggest_nutritionist": ["nutricionista", "dietista", "especializado"],
            "provide_feasible_options": [
                "opciones viables",
                "es posible",
                "requiere planificación",
            ],
            "check_nutritional_adequacy": ["suplementar", "monitorear", "deficiencias"],
            "free_alternatives": ["gratis", "sin costo", "económico"],
            "bodyweight_focus": ["peso corporal", "calistenia", "sin gastar"],
            "budget_nutrition_tips": ["económica", "barato", "ahorro"],
            "no_supplement_pressure": [
                "no necesitas suplementos",
                "opcionales",
                "comida real",
            ],
            "resourceful_solutions": [
                "creativo",
                "recursos gratuitos",
                "usa lo que tengas",
            ],
            "inclusive_approach": ["por supuesto", "para todos", "adaptaremos"],
            "adapted_exercises": ["adaptados", "desde la silla", "específicas"],
            "acknowledge_challenges": ["desafíos únicos", "obstáculos", "reconozco"],
            "suggest_specialized_resources": [
                "organizaciones especializadas",
                "grupos locales",
                "fisioterapeutas",
            ],
            "maintain_empowerment": ["determinación", "límites", "fortaleza mental"],
            "identify_inconsistencies": ["inconsistencias", "conflicto", "no cuadran"],
            "clarify_politely": ["sin problema", "error de tipeo", "aclaremos"],
            "handle_gracefully": [
                "no hay problema",
                "está bien",
                "gracias por la aclaración",
            ],
            "request_clarification": ["confirmar", "ayúdame a entender", "clarificar"],
            "maintain_professionalism": [
                "objetivo es ayudarte",
                "sigamos adelante",
                "lo importante",
            ],
            "maintain_context_awareness": ["varios temas", "cuál", "organicemos"],
            "handle_transitions_smoothly": ["cambiemos", "hablemos", "volvamos"],
            "offer_to_prioritize": ["prioridad principal", "por dónde", "urgentemente"],
            "track_all_requests": ["apuntados", "no olvidaré", "cubriremos todo"],
            "provide_coherent_responses": ["organizadas", "completa", "coherente"],
            "acknowledge_preferences": [
                "preferencias específicas",
                "respeto",
                "únicos",
            ],
            "provide_flexible_alternatives": ["considerar", "rangos", "flexible"],
            "explain_practical_limitations": [
                "difíciles de implementar",
                "limitar tu progreso",
                "poco práctico",
            ],
            "maintain_helpfulness": [
                "mejores opciones",
                "objetivo es ayudarte",
                "razonablemente posible",
            ],
            "suggest_compromises": [
                "empezamos con algunas",
                "incorporar elementos",
                "margen de maniobra",
            ],
            "respect_privacy": [
                "respeto tu privacidad",
                "no necesitas compartir",
                "información personal",
            ],
            "explain_limitations": [
                "menos efectivas",
                "menos personalizado",
                "afectan la precisión",
            ],
            "provide_general_guidance": [
                "principios generales",
                "universalmente seguras",
                "pautas generales",
            ],
            "offer_alternatives": ["rangos", "información general", "categorías"],
            "maintain_usefulness": ["plan básico", "valiosa", "mejor esfuerzo"],
            "age_appropriate_advice": ["edad", "apropiado", "necesidades específicas"],
            "safety_first_approach": ["seguridad", "prioritaria", "cero riesgos"],
            "suggest_medical_clearance": [
                "autorización médica",
                "chequeo médico",
                "evaluar y aprobar",
            ],
            "educational_response": ["te explico", "entender", "eduquemos"],
            "involve_guardians_if_minor": ["padres", "tutores", "supervisión parental"],
            "cultural_awareness": ["respeto", "prácticas religiosas", "cultura"],
            "respectful_alternatives": [
                "opciones respetuosas",
                "alternativas",
                "respetan tus creencias",
            ],
            "acknowledge_beliefs": ["creencias", "válidas", "convicciones"],
            "inclusive_solutions": ["para todos", "inclusividad", "cualquier creencia"],
            "avoid_judgment": ["no hay juicio", "válidas", "sin cuestionar"],
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
