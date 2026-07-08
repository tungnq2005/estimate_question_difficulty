"""
Anh 9 ontology generator.

*** DIFFERENT FRAMEWORK — please read ***

English as a SECOND LANGUAGE is not a knowledge domain like STEM subjects.
There are no "facts to memorize" in the same sense. Instead, English is
SKILL-based: learners acquire structures, vocabulary, and functions that
compose into reading/listening/writing/speaking ability.

Therefore the ontology here captures:
  - Grammar structures with their CEFR level and prerequisite chain
  - Vocabulary topics (thematic word groups)
  - Language functions (describing, comparing, requesting...)
  - Skill types (reading, listening, writing, speaking)
  - Text types (formal letter, narrative, report...)

Difficulty drivers:
  (a) CEFR level of grammar structure (A1 -> A2 -> B1),
  (b) vocabulary frequency rank (common words easier than rare),
  (c) sentence/passage length,
  (d) topic familiarity (exam topic list vs obscure domain),
  (e) multi-skill demand (e.g. reading + writing response).

Classes:
  - GrammarStructure:  cau truc ngu phap
  - VocabularyTopic:   chu de tu vung
  - LanguageFunction:  chuc nang ngon ngu
  - SkillType:         ky nang
  - TextType:          the loai van ban
  - LessonUnit, Textbook

CAUTION: English content is STRUCTURED DIFFERENTLY from other subjects.
Paper should discuss why this schema suits a skill-based subject.
"""

from pathlib import Path
ROOT = Path(__file__).resolve().parent

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix eng:  <http://edu.vn/eng9/ontology#> .

<http://edu.vn/eng9/ontology> a owl:Ontology ;
    rdfs:label "Ontology Tieng Anh 9 - Cold-start Question Difficulty Estimation"@vi ;
    owl:versionInfo "0.1.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

eng:EngEntity         a owl:Class ; rdfs:label "Thuc the Tieng Anh"@vi .
eng:GrammarStructure  a owl:Class ; rdfs:subClassOf eng:EngEntity ; rdfs:label "Cau truc ngu phap"@vi .
eng:VocabularyTopic   a owl:Class ; rdfs:subClassOf eng:EngEntity ; rdfs:label "Chu de tu vung"@vi .
eng:LanguageFunction  a owl:Class ; rdfs:subClassOf eng:EngEntity ; rdfs:label "Chuc nang ngon ngu"@vi .
eng:SkillType         a owl:Class ; rdfs:subClassOf eng:EngEntity ; rdfs:label "Ky nang"@vi .
eng:TextType          a owl:Class ; rdfs:subClassOf eng:EngEntity ; rdfs:label "The loai van ban"@vi .
eng:LessonUnit        a owl:Class ; rdfs:label "Bai hoc SGK"@vi .
eng:Textbook          a owl:Class ; rdfs:label "Bo SGK"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

eng:prerequisiteOf a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:label "la tien de cua"@vi .
eng:specializesGrammar a owl:ObjectProperty ;
    rdfs:domain eng:GrammarStructure ; rdfs:range eng:GrammarStructure ;
    rdfs:label "la truong hop dac biet cua"@vi .

eng:requires a owl:ObjectProperty ; rdfs:label "doi hoi"@vi .
eng:expresses a owl:ObjectProperty ;
    rdfs:domain eng:GrammarStructure ; rdfs:range eng:LanguageFunction ;
    rdfs:label "dien dat chuc nang"@vi .

eng:usesGrammar a owl:ObjectProperty ;
    rdfs:domain eng:TextType ; rdfs:range eng:GrammarStructure ;
    rdfs:label "su dung cau truc"@vi .

eng:usesVocabulary a owl:ObjectProperty ;
    rdfs:domain eng:TextType ; rdfs:range eng:VocabularyTopic ;
    rdfs:label "su dung tu vung chu de"@vi .

eng:relatedVocab a owl:ObjectProperty , owl:SymmetricProperty ;
    rdfs:domain eng:VocabularyTopic ; rdfs:range eng:VocabularyTopic ;
    rdfs:label "chu de tu vung lien quan"@vi .

eng:appearsInLesson a owl:ObjectProperty ; rdfs:range eng:LessonUnit ; rdfs:label "xuat hien trong bai"@vi .
eng:partOfTextbook a owl:ObjectProperty ; rdfs:range eng:Textbook ; rdfs:label "thuoc bo SGK"@vi .

eng:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong tu"@vi .
eng:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "doi lap"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

eng:cefrLevel a owl:DatatypeProperty ; rdfs:range xsd:string ;
    rdfs:comment "CEFR level: A1, A2, B1, B2 (most 9th-grade content is A2-B1)"@vi .
eng:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer .
eng:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer .
eng:structuralComplexity a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "Do phuc tap cau truc: 1=don, 5=nhieu tang (embedded clauses)"@vi .
eng:frequencyBand a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "Band tan suat tu vung: 1=high-freq (A1), 5=low-freq (B2+)"@vi .
eng:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer .
eng:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer .
eng:aliases a owl:DatatypeProperty ; rdfs:range xsd:string .
eng:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer .

#################################################################
#   TEXTBOOKS
#################################################################

eng:TB_Old a eng:Textbook ; rdfs:label "SGK Tieng Anh 9 (bo cu, 7 nam)"@vi ; eng:confidence 3 .
eng:TB_ThiDiem a eng:Textbook ; rdfs:label "SGK Tieng Anh 9 (thi diem, 10 nam)"@vi ; eng:confidence 3 .
eng:TB_GlobalSuccess a eng:Textbook ; rdfs:label "Global Success 9"@vi ; eng:confidence 3 .
eng:TB_Friends a eng:Textbook ; rdfs:label "iLearn Smart World / Friends Plus 9"@vi ; eng:confidence 2 .
"""

# ======================================================================
# DATA
# ======================================================================

# --- Grammar structures ---
GRAMMAR = [
    # id, label, aliases, cefr, complexity, abstract, bloom, conf
    ("GR_PresentSimple", "Present Simple tense", "Hien tai don", "A1", 1, 2, 2, 3),
    ("GR_PresentContinuous", "Present Continuous tense", "Hien tai tiep dien", "A1", 2, 2, 2, 3),
    ("GR_PresentPerfect", "Present Perfect tense", "Hien tai hoan thanh", "A2", 3, 3, 3, 3),
    ("GR_PresentPerfectContinuous", "Present Perfect Continuous tense", "HTHTTD", "B1", 4, 3, 3, 3),
    ("GR_PastSimple", "Past Simple tense", "Qua khu don", "A1", 2, 2, 2, 3),
    ("GR_PastContinuous", "Past Continuous tense", "Qua khu tiep dien", "A2", 3, 3, 2, 3),
    ("GR_PastPerfect", "Past Perfect tense", "Qua khu hoan thanh", "B1", 3, 3, 3, 3),
    ("GR_FutureSimple", "Future Simple (will / shall)", "Tuong lai don", "A1", 2, 2, 2, 3),
    ("GR_FutureGoingTo", "Future with 'be going to'", "", "A1", 2, 2, 2, 3),
    ("GR_Modals", "Modal verbs (can/could/should/must/may)", "Dong tu khuyet thieu", "A2", 3, 3, 3, 3),
    ("GR_Passive", "Passive voice (general)", "Cau bi dong", "A2", 3, 3, 3, 3),
    ("GR_Passive_Tenses", "Passive in different tenses", "Bi dong cac thi", "B1", 4, 3, 3, 3),
    ("GR_Cond_0", "Zero conditional (if + present, present)", "Dieu kien loai 0", "A2", 3, 3, 3, 3),
    ("GR_Cond_1", "First conditional (if + present, will)", "Dieu kien loai 1", "A2", 3, 3, 3, 3),
    ("GR_Cond_2", "Second conditional (if + past, would)", "Dieu kien loai 2", "B1", 4, 4, 3, 3),
    ("GR_Cond_3", "Third conditional (if + past perfect, would have)", "Dieu kien loai 3", "B1", 5, 4, 4, 3),
    ("GR_Reported", "Reported speech", "Cau tuong thuat", "B1", 4, 4, 3, 3),
    ("GR_Relative_Defining", "Defining relative clauses (who/which/that)", "Menh de quan he xac dinh", "A2", 3, 3, 3, 3),
    ("GR_Relative_NonDef", "Non-defining relative clauses", "Menh de quan he khong xac dinh", "B1", 4, 3, 3, 3),
    ("GR_Wishes", "Wishes (I wish / If only)", "Cau uoc", "B1", 4, 4, 3, 3),
    ("GR_PhrasalVerbs", "Phrasal verbs", "Cum dong tu", "B1", 3, 3, 3, 3),
    ("GR_Gerund_Inf", "Gerund vs infinitive", "V-ing vs to-V", "A2", 3, 3, 3, 3),
    ("GR_Comparisons", "Comparatives and superlatives", "So sanh hon va nhat", "A1", 2, 2, 2, 3),
    ("GR_ComparisonAs", "Comparisons with 'as...as'", "So sanh bang", "A2", 2, 2, 2, 3),
    ("GR_Articles", "Articles (a/an/the)", "Mao tu", "A1", 2, 3, 2, 3),
    ("GR_Prepositions", "Prepositions (time, place, direction)", "Gioi tu", "A1", 2, 2, 2, 3),
    ("GR_Connectors", "Connectors / Linking words (and/but/so/because/although)", "Tu noi", "A2", 3, 3, 3, 3),
    ("GR_Connectors_Adv", "Advanced connectors (however, nevertheless, despite, in spite of)", "Tu noi nang cao", "B1", 4, 3, 3, 3),
    ("GR_Tag", "Tag questions", "Cau hoi duoi", "A2", 3, 3, 3, 3),
]

# --- Vocabulary topics ---
VOCAB = [
    # id, label, aliases, band, freq, abstract, conf
    ("V_LocalEnvironment", "Local environment (tradition, craft, village)", "", 3, 8, 2, 3),
    ("V_CityLife", "City life", "", 2, 7, 2, 3),
    ("V_TeenLife", "Teen life / adolescents", "", 3, 7, 3, 3),
    ("V_LearningLanguages", "Learning a foreign language", "", 3, 6, 3, 3),
    ("V_VNWonders", "Wonders of Vietnam / World", "", 3, 6, 2, 3),
    ("V_VNThenAndNow", "Vietnam then and now", "", 3, 6, 3, 3),
    ("V_Food_Recipes", "Recipes and eating habits", "Food and drink", 2, 6, 2, 3),
    ("V_Tourism", "Tourism / travel", "", 2, 7, 2, 3),
    ("V_EnglishInTheWorld", "English in the world", "", 3, 5, 3, 3),
    ("V_SpaceTravel", "Space travel / exploration", "", 4, 5, 3, 3),
    ("V_ChangingRoles", "Changing roles in society (gender, work)", "", 4, 5, 4, 3),
    ("V_MyFutureCareer", "My future career / jobs", "", 3, 6, 3, 3),
    ("V_Environment", "Environment and pollution", "", 3, 7, 3, 3),
    ("V_Education", "Education", "", 3, 6, 3, 3),
    ("V_Technology", "Technology / computers / communication", "", 3, 6, 3, 3),
    ("V_Health", "Health and illness", "", 3, 5, 2, 3),
    ("V_Entertainment", "Entertainment (films, music)", "", 2, 5, 2, 3),
    ("V_CulturesCountries", "Cultures and countries", "", 3, 6, 3, 3),
]

# --- Language functions ---
FUNCTIONS = [
    ("LF_Describing", "Describing (people, places, things)", "", 2, 2, 3),
    ("LF_Comparing", "Comparing / contrasting", "", 2, 2, 3),
    ("LF_GivingOpinion", "Giving and justifying opinions", "", 3, 3, 3),
    ("LF_AgreeDisagree", "Agreeing and disagreeing", "", 3, 3, 3),
    ("LF_Suggesting", "Making suggestions / recommendations", "", 3, 3, 3),
    ("LF_Requesting", "Making requests and offers", "", 3, 3, 3),
    ("LF_GivingAdvice", "Giving advice", "", 3, 3, 3),
    ("LF_TalkingAboutPast", "Talking about past experiences / events", "", 3, 3, 3),
    ("LF_TalkingAboutFuture", "Talking about future plans / predictions", "", 3, 3, 3),
    ("LF_HypotheticalThinking", "Hypothetical / imaginary thinking", "", 4, 4, 3),
    ("LF_Narrating", "Narrating a story / sequence of events", "", 3, 3, 3),
    ("LF_Persuading", "Persuading", "", 4, 4, 3),
]

# --- Skill types ---
SKILLS = [
    ("SK_Reading", "Reading comprehension", "", 3, 2, 3),
    ("SK_Listening", "Listening comprehension", "", 3, 2, 3),
    ("SK_Writing", "Writing", "", 3, 3, 3),
    ("SK_Speaking", "Speaking", "", 3, 3, 3),
    ("SK_GrammarVocabUse", "Use of English (grammar & vocabulary)", "Use of English", 3, 3, 3),
]

# --- Text types ---
TEXT_TYPES = [
    ("TT_FormalLetter", "Formal letter / email", "", 3, 3, 3),
    ("TT_InformalLetter", "Informal letter / email", "", 2, 2, 3),
    ("TT_Narrative", "Narrative (story)", "", 3, 3, 3),
    ("TT_Descriptive", "Descriptive text (person/place)", "", 2, 2, 3),
    ("TT_OpinionEssay", "Opinion essay", "", 4, 4, 3),
    ("TT_ForAgainstEssay", "For-and-against essay", "", 4, 4, 3),
    ("TT_Report", "Report", "", 3, 3, 3),
    ("TT_Article", "Article (newspaper/magazine)", "", 3, 3, 3),
    ("TT_Dialogue", "Dialogue / conversation", "", 2, 2, 3),
    ("TT_Announcement", "Announcement / notice", "", 2, 2, 3),
]

print(f'Anh: {len(GRAMMAR)} grammar, {len(VOCAB)} vocab, {len(FUNCTIONS)} functions, '
      f'{len(SKILLS)} skills, {len(TEXT_TYPES)} text types')


# ======================================================================
# LESSONS (thi diem, 12 units typical)
# ======================================================================
LESSONS_OLD = [
    (1, "A visit from a pen pal"),
    (2, "Clothing"),
    (3, "A trip to the countryside"),
    (4, "Learning a foreign language"),
    (5, "The media"),
    (6, "The environment"),
    (7, "Saving energy"),
    (8, "Celebrations"),
    (9, "Natural disasters"),
    (10, "Life on other planets"),
]

LESSONS_ThiDiem = [
    (1, "Local environment"),
    (2, "City life"),
    (3, "Teen stress and pressure"),
    (4, "Life in the past"),
    (5, "Wonders of Vietnam"),
    (6, "Vietnam then and now"),
    (7, "Recipes and eating habits"),
    (8, "Tourism"),
    (9, "English in the world"),
    (10, "Space travel"),
    (11, "Changing roles in society"),
    (12, "My future career"),
]

LESSONS_GS = [(i, f"Global Success 9 Unit {i}") for i in range(1, 13)]
LESSONS_Friends = [(i, f"iLearn/Friends+ 9 Unit {i}") for i in range(1, 13)]

# ======================================================================
# RELATIONSHIPS
# ======================================================================

# Grammar prerequisites (teaching order)
PREREQUISITES = [
    # Tense chain
    ("GR_PresentSimple", "GR_PresentContinuous"),
    ("GR_PresentSimple", "GR_PastSimple"),
    ("GR_PresentSimple", "GR_FutureSimple"),
    ("GR_PresentSimple", "GR_FutureGoingTo"),
    ("GR_PresentSimple", "GR_PresentPerfect"),
    ("GR_PresentPerfect", "GR_PresentPerfectContinuous"),
    ("GR_PastSimple", "GR_PastContinuous"),
    ("GR_PastSimple", "GR_PastPerfect"),
    ("GR_PastSimple", "GR_Passive"),
    ("GR_Passive", "GR_Passive_Tenses"),
    # Conditionals chain
    ("GR_PresentSimple", "GR_Cond_0"),
    ("GR_Cond_0", "GR_Cond_1"),
    ("GR_PastSimple", "GR_Cond_2"),
    ("GR_Cond_1", "GR_Cond_2"),
    ("GR_PastPerfect", "GR_Cond_3"),
    ("GR_Cond_2", "GR_Cond_3"),
    ("GR_Cond_2", "GR_Wishes"),
    # Reported speech
    ("GR_PastSimple", "GR_Reported"),
    ("GR_Modals", "GR_Reported"),
    # Relative clauses
    ("GR_Relative_Defining", "GR_Relative_NonDef"),
    # Comparisons
    ("GR_Comparisons", "GR_ComparisonAs"),
    # Basics
    ("GR_Articles", "GR_PresentSimple"),
    ("GR_Prepositions", "GR_PresentSimple"),
    ("GR_Connectors", "GR_Connectors_Adv"),
]

# specializesGrammar
SPEC_GRAMMAR = [
    ("GR_Passive_Tenses", "GR_Passive"),  # passive in various tenses is specialization of passive
    ("GR_Relative_NonDef", "GR_Relative_Defining"),
]

# Grammar expresses Language function
EXPRESSES = [
    ("GR_PresentSimple", "LF_Describing"),
    ("GR_PresentContinuous", "LF_Describing"),
    ("GR_PastSimple", "LF_Narrating"),
    ("GR_PastSimple", "LF_TalkingAboutPast"),
    ("GR_PastContinuous", "LF_Narrating"),
    ("GR_PresentPerfect", "LF_TalkingAboutPast"),
    ("GR_FutureSimple", "LF_TalkingAboutFuture"),
    ("GR_FutureGoingTo", "LF_TalkingAboutFuture"),
    ("GR_Cond_1", "LF_TalkingAboutFuture"),
    ("GR_Cond_2", "LF_HypotheticalThinking"),
    ("GR_Cond_3", "LF_HypotheticalThinking"),
    ("GR_Wishes", "LF_HypotheticalThinking"),
    ("GR_Modals", "LF_GivingAdvice"),
    ("GR_Modals", "LF_Requesting"),
    ("GR_Modals", "LF_Suggesting"),
    ("GR_Comparisons", "LF_Comparing"),
    ("GR_ComparisonAs", "LF_Comparing"),
    ("GR_Reported", "LF_Narrating"),
]

# Text types use grammar
USES_GRAMMAR = [
    ("TT_Narrative", "GR_PastSimple"),
    ("TT_Narrative", "GR_PastContinuous"),
    ("TT_Narrative", "GR_PastPerfect"),
    ("TT_Narrative", "GR_Connectors"),
    ("TT_Descriptive", "GR_PresentSimple"),
    ("TT_Descriptive", "GR_Relative_Defining"),
    ("TT_Descriptive", "GR_Comparisons"),
    ("TT_OpinionEssay", "GR_Modals"),
    ("TT_OpinionEssay", "GR_Connectors_Adv"),
    ("TT_OpinionEssay", "GR_Cond_2"),
    ("TT_ForAgainstEssay", "GR_Connectors_Adv"),
    ("TT_ForAgainstEssay", "GR_Passive"),
    ("TT_FormalLetter", "GR_Modals"),
    ("TT_FormalLetter", "GR_Passive"),
    ("TT_InformalLetter", "GR_PresentPerfect"),
    ("TT_Report", "GR_Passive"),
    ("TT_Report", "GR_PresentSimple"),
    ("TT_Article", "GR_Relative_Defining"),
    ("TT_Article", "GR_Passive"),
    ("TT_Dialogue", "GR_Tag"),
    ("TT_Dialogue", "GR_Modals"),
]

# Text types use vocabulary topic (examples)
USES_VOCAB = [
    ("TT_Article", "V_VNWonders"),
    ("TT_Article", "V_Environment"),
    ("TT_Report", "V_Environment"),
    ("TT_Report", "V_Education"),
    ("TT_Narrative", "V_TeenLife"),
    ("TT_OpinionEssay", "V_ChangingRoles"),
    ("TT_OpinionEssay", "V_Technology"),
    ("TT_FormalLetter", "V_Tourism"),
    ("TT_FormalLetter", "V_MyFutureCareer"),
    ("TT_Descriptive", "V_LocalEnvironment"),
    ("TT_Descriptive", "V_CityLife"),
    ("TT_Descriptive", "V_VNWonders"),
]

# Related vocab (thematic neighbors)
RELATED_VOCAB = [
    ("V_LocalEnvironment", "V_CityLife"),
    ("V_VNWonders", "V_Tourism"),
    ("V_VNThenAndNow", "V_VNWonders"),
    ("V_SpaceTravel", "V_Technology"),
    ("V_Health", "V_Food_Recipes"),
    ("V_Environment", "V_LocalEnvironment"),
    ("V_MyFutureCareer", "V_Education"),
    ("V_ChangingRoles", "V_TeenLife"),
    ("V_EnglishInTheWorld", "V_CulturesCountries"),
]

# Similarities for comparison questions
SIMILARITIES = [
    ("GR_PresentSimple", "GR_PresentContinuous"),
    ("GR_PastSimple", "GR_PastContinuous"),
    ("GR_Cond_1", "GR_Cond_2"),
    ("GR_Cond_2", "GR_Cond_3"),
    ("GR_Relative_Defining", "GR_Relative_NonDef"),
    ("TT_FormalLetter", "TT_InformalLetter"),
    ("TT_OpinionEssay", "TT_ForAgainstEssay"),
]

CONTRASTS = [
    ("GR_PresentSimple", "GR_PresentContinuous"),
    ("GR_Cond_1", "GR_Cond_2"),
    ("GR_Passive", "GR_Passive"),
    ("GR_Gerund_Inf", "GR_Gerund_Inf"),
    ("TT_FormalLetter", "TT_InformalLetter"),
]

# Remove self-contrasts
CONTRASTS = [(a, b) for a, b in CONTRASTS if a != b]

print(f'  + {len(PREREQUISITES)} prereq, {len(SPEC_GRAMMAR)} spec, '
      f'{len(EXPRESSES)} expresses, {len(USES_GRAMMAR)} uses-gramm, '
      f'{len(USES_VOCAB)} uses-vocab, {len(RELATED_VOCAB)} related-vocab, '
      f'{len(SIMILARITIES)} sim, {len(CONTRASTS)} contrast')
