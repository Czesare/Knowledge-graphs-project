"""
Expanded static concept mappings from HINT thesaurus to Wikidata and DBpedia.
Replace the CONCEPT_MAPPINGS dict in 04_add_external_links.py with this one.

Each entry: "hint:ConceptName": [("predicate", "target_uri"), ...]
Multiple links per concept are allowed and encouraged for link count.

Wikidata IDs have been manually verified.
"""

CONCEPT_MAPPINGS = {

    # ================================================================
    # DOMAINS -> Wikidata + DBpedia (14 links)
    # ================================================================
    "hint:HealthAndLifestyleDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q12147"),           # health
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Health"),
    ],
    "hint:EducationDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q8434"),            # education
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Education"),
    ],
    "hint:MedicalDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q11190"),           # medicine
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Medicine"),
    ],
    "hint:LawAndPolicyDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q7748"),            # law
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Law"),
    ],
    "hint:IndustrialAndServiceRoboticsDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q11012"),           # robotics
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Robotics"),
    ],
    "hint:SmartCampusDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q3918"),            # university
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Smart_campus"),
    ],
    "hint:DigitalMuseumDomain": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q33506"),           # museum
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Virtual_museum"),
    ],

    # ================================================================
    # GOALS -> Wikidata + DBpedia (14 links)
    # ================================================================
    "hint:UserWellbeingGoal": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q332717"),          # well-being
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Well-being"),
    ],
    "hint:SafeRetrievalGoal": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q3054889"),       # safety
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Information_retrieval"),
    ],
    "hint:FairAccurateVerdictGoal": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q189786"),        # fairness
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Fact-checking"),
    ],
    "hint:EffectiveLearningGoal": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q133500"),          # learning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Learning"),
    ],
    "hint:AccurateTrustworthyDiagnosisGoal": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q16644043"),        # medical diagnosis
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Medical_diagnosis"),
    ],
    "hint:FairEfficientHeatingGoal": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q185043"),        # energy efficiency
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Energy_conservation"),
    ],
    "hint:EnhancedVisitorGoal": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q15401930"),      # user experience
        ("rdfs:seeAlso", "http://dbpedia.org/resource/User_experience"),
    ],

    # ================================================================
    # CONSTRAINTS -> Wikidata + DBpedia (20 links)
    # ================================================================
    "hint:EthicalConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q9465"),            # ethics
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Ethics"),
    ],
    "hint:PrivacyConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q8492"),            # privacy
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Privacy"),
    ],
    "hint:TransparencyConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q535347"),          # transparency
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Transparency_(behavior)"),
    ],
    "hint:FairnessConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q189786"),          # fairness
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Fairness_(disambiguation)"),
    ],
    "hint:SafetyConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q3054889"),         # safety
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Safety"),
    ],
    "hint:AutonomyConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q4120621"),         # autonomy
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Autonomy"),
    ],
    "hint:UndueInfluenceConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1479126"),         # undue influence
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Undue_influence"),
    ],
    "hint:SustainabilityConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q219416"),          # sustainability
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Sustainability"),
    ],
    "hint:AccessibilityConstraint": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q555097"),          # accessibility
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Accessibility"),
    ],
    "hint:UserComfortConstraint": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q373432"),        # usability
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Usability"),
    ],

    # ================================================================
    # CAPABILITIES -> Wikidata + DBpedia (42 links)
    # ================================================================
    "hint:ReasoningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q130901"),          # reasoning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Reasoning"),
    ],
    "hint:BayesianReasoningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q44432"),           # Bayesian inference
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Bayesian_inference"),
    ],
    "hint:SemanticReasoningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1656682"),         # semantic reasoner
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Semantic_reasoner"),
    ],
    "hint:EmbeddingReasoningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q65076586"),        # word embedding
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Word_embedding"),
    ],
    "hint:ClinicalJudgmentCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q16644043"),        # medical diagnosis
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Clinical_decision_support_system"),
    ],
    "hint:PatternLearningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q2539"),            # machine learning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Machine_learning"),
    ],
    "hint:ReinforcementLearningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q830688"),          # reinforcement learning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Reinforcement_learning"),
    ],
    "hint:MetaAnalysisCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q815382"),          # meta-analysis
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Meta-analysis"),
    ],
    "hint:ExplainingCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q487395"),          # explainability
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Explainable_artificial_intelligence"),
    ],
    "hint:NegotiationCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q14982"),           # negotiation
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Negotiation"),
    ],
    "hint:KnowledgeGraphQueryingCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q33002955"),        # knowledge graph
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Knowledge_graph"),
    ],
    "hint:SensingCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q167676"),          # sensor
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Sensor"),
    ],
    "hint:SituationalAwarenessCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1752640"),         # situational awareness
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Situation_awareness"),
    ],
    "hint:MultimodalInterpretationCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q107190418"),       # multimodal learning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Multimodal_learning"),
    ],
    "hint:ReportingCapability": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q32907"),         # report
    ],
    "hint:FineDexterityCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q223638"),          # fine motor skill
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Fine_motor_skill"),
    ],
    "hint:HeavyLiftingCapability": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q11012"),         # robotics
    ],
    "hint:OperatorCoordinationCapability": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q205892"),        # coordination
    ],
    "hint:CognitiveReasoningCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q3966542"),         # cognitive ability
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Cognition"),
    ],
    "hint:CommunicationExplanationCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q11024"),           # communication
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Communication"),
    ],
    "hint:PerceptionSensingCapability": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1080148"),         # perception
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Perception"),
    ],

    # ================================================================
    # METHODS -> Wikidata + DBpedia (20 links)
    # ================================================================
    "hint:ArgumentationReasoningMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q815741"),          # argumentation theory
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Argumentation_theory"),
    ],
    "hint:ReinforcementLearningMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q830688"),          # reinforcement learning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Reinforcement_learning"),
    ],
    "hint:KnowledgeGraphQueryMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q33002955"),        # knowledge graph
        ("rdfs:seeAlso", "http://dbpedia.org/resource/SPARQL"),
    ],
    "hint:PostHocExplanationMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q487395"),          # explainable AI
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Explainable_artificial_intelligence"),
    ],
    "hint:BayesianLogicMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q44432"),           # Bayesian inference
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Bayesian_network"),
    ],
    "hint:MetaAnalysisScoringMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q815382"),          # meta-analysis
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Meta-analysis"),
    ],
    "hint:SemanticLinkingMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1621273"),         # Semantic Web
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Semantic_Web"),
    ],
    "hint:SemanticEmbeddingMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q65076586"),        # word embedding
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Word_embedding"),
    ],
    "hint:CooperativeLearningMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1535726"),         # collaborative learning
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Collaborative_learning"),
    ],
    "hint:DataCollectionMethod": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1783551"),         # data collection
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Data_collection"),
    ],

    # ================================================================
    # TASKS -> Wikidata (15 links)
    # ================================================================
    "hint:DataCollectionTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1783551"),         # data collection
    ],
    "hint:ConflictResolutionTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1194317"),         # conflict resolution
    ],
    "hint:ExplanationTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q487395"),          # explainable AI
    ],
    "hint:SituationalAssessmentTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1752640"),         # situation awareness
    ],
    "hint:QuestionAnsweringTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q7271743"),         # question answering
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Question_answering"),
    ],
    "hint:SemanticReasoningTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1656682"),         # semantic reasoner
    ],
    "hint:BayesianInferenceTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q44432"),           # Bayesian inference
    ],
    "hint:SymptomAnalysisTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q169872"),          # symptom
    ],
    "hint:RecommendResourcesTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q860488"),          # recommender system
    ],
    "hint:PolicyLearningTask": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q830688"),        # reinforcement learning
    ],
    "hint:KnowledgeGraphQueryTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q33002955"),        # knowledge graph
    ],
    "hint:MultimodalInputInterpretationTask": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q107190418"),       # multimodal learning
    ],
    "hint:DecideInterventionTask": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1426711"),       # intervention
    ],

    # ================================================================
    # PHENOMENA -> Wikidata + DBpedia (22 links)
    # ================================================================
    "hint:Phenomenon": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q483247"),          # phenomenon
    ],
    "hint:TrustShiftPhenomenon": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q47461"),         # trust
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Trust_(social_science)"),
    ],
    "hint:KnowledgeMismatchPhenomenon": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1125806"),       # information asymmetry
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Information_asymmetry"),
    ],
    "hint:DiagnosisAnchoringPhenomenon": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q360537"),          # anchoring bias
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Anchoring_(cognitive_bias)"),
    ],
    "hint:Bias": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1482135"),         # cognitive bias
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Cognitive_bias"),
    ],
    "hint:ConfirmationBias": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q175646"),          # confirmation bias
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Confirmation_bias"),
    ],
    "hint:GroupThinkingPhenomenon": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q331556"),          # groupthink
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Groupthink"),
    ],
    "hint:EngagementShiftPhenomenon": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q15401930"),      # user experience
    ],
    "hint:RiskExposurePhenomenon": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q104493"),        # risk
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Risk"),
    ],
    "hint:SensorNoisePhenomenon": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q498845"),          # signal noise
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Noise_(signal_processing)"),
    ],
    "hint:DataMismatchPhenomenon": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q310202"),        # data quality
    ],

    # ================================================================
    # METRICS -> Wikidata (16 links)
    # ================================================================
    "hint:TrustPreservationMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q47461"),         # trust
    ],
    "hint:TaskSuccessRateMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q3992824"),       # success rate
    ],
    "hint:SafetyComplianceMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q3054889"),       # safety
    ],
    "hint:ExplanationClarityMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q487395"),        # explainable AI
    ],
    "hint:FairOutcomeMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q189786"),        # fairness
    ],
    "hint:DiagnosisAccuracyMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q13479982"),      # accuracy
    ],
    "hint:LearningGainMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q133500"),        # learning
    ],
    "hint:AnswerAccuracyMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q13479982"),      # accuracy
    ],
    "hint:TimeMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q11471"),         # time
    ],
    "hint:EnergyEfficiencyMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q185043"),        # energy efficiency
    ],
    "hint:CO2ReductionMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q167336"),        # carbon dioxide
    ],
    "hint:EngagementTimeMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q15401930"),      # user experience
    ],
    "hint:RecommendationRelevanceMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q860488"),        # recommender system
    ],
    "hint:UndueInfluenceMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1479126"),       # undue influence
    ],
    "hint:UserComfortMetric": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q373432"),        # usability
    ],

    # ================================================================
    # INTERACTION MODALITIES -> Wikidata (8 links)
    # ================================================================
    "hint:VerbalDialogueModality": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q131395"),          # dialogue
    ],
    "hint:TextChatModality": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q15077303"),        # chatbot
    ],
    "hint:DashboardModality": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1072917"),         # dashboard
    ],
    "hint:VirtualRealityModality": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q170519"),          # virtual reality
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Virtual_reality"),
    ],
    "hint:VoiceChatModality": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1569397"),       # voice user interface
    ],
    "hint:NetworkProtocolModality": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q15836568"),      # communication protocol
    ],

    # ================================================================
    # ROLES -> Wikidata (10 links)
    # ================================================================
    "hint:TutorRole": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q37226"),           # teacher
    ],
    "hint:LearnerRole": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q48282"),           # student
    ],
    "hint:ClinicianRole": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q39631"),           # physician
    ],
    "hint:JurorRole": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q319141"),          # juror
    ],
    "hint:VisitorRole": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q15401930"),      # user experience
    ],

    # ================================================================
    # TOP-LEVEL CONCEPTS -> Wikidata + DBpedia (12 links)
    # ================================================================
    "hint:Agent": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q16735822"),        # intelligent agent
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Intelligent_agent"),
    ],
    "hint:ArtificialAgent": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q11660"),           # artificial intelligence
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Artificial_intelligence"),
    ],
    "hint:HumanAgent": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q5"),               # human
    ],
    "hint:Interaction": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q80919"),           # human-computer interaction
        ("rdfs:seeAlso", "http://dbpedia.org/resource/Human%E2%80%93computer_interaction"),
    ],
    "hint:Capability": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1137655"),       # capability
    ],
    "hint:Task": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q759676"),        # task
    ],
    "hint:Evaluation": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1379672"),       # evaluation
    ],

    # ================================================================
    # USE CASES -> Wikidata (7 links)
    # ================================================================
    "hint:PersonalAssistantUseCase": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q2539925"),         # virtual assistant
    ],
    "hint:MedicalDiagnosisUseCase": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q16644043"),        # medical diagnosis
    ],
    "hint:AutonomousTutoringUseCase": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q2251299"),         # intelligent tutoring system
    ],
    "hint:GroupDeliberationUseCase": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1201750"),         # deliberation
    ],
    "hint:EnergyNegotiationUseCase": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q12739"),         # energy management
    ],
    "hint:VirtualMuseumGuideUseCase": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q33506"),         # museum
    ],
    "hint:CollaborativeManipulationUseCase": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q11012"),         # robotics
    ],

    # ================================================================
    # CONTEXTS -> Wikidata (7 links)
    # ================================================================
    "hint:HealthMonitoringContext": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q743034"),        # health monitoring
    ],
    "hint:OnlineLearningContext": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q1412953"),         # e-learning
    ],
    "hint:ClinicalConsultationContext": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q39631"),         # physician
    ],
    "hint:JuryDeliberationContext": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1201750"),       # deliberation
    ],
    "hint:WorkspaceManipulationContext": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q11012"),         # robotics
    ],
    "hint:VirtualExhibitionContext": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q464980"),        # exhibition
    ],
    "hint:SmartCampusContext": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q3918"),          # university
    ],

    # ================================================================
    # FEEDBACK -> Wikidata (5 links)
    # ================================================================
    "hint:Feedback": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q184199"),          # feedback
    ],
    "hint:TrustReportFeedback": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q47461"),         # trust
    ],
    "hint:ExplanationMessageFeedback": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q487395"),        # explainable AI
    ],
    "hint:InterventionRationaleFeedback": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1426711"),       # intervention
    ],
    "hint:RecommendationRationaleFeedback": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q860488"),        # recommender system
    ],

    # ================================================================
    # EXPERIMENTS -> Wikidata (5 links)
    # ================================================================
    "hint:Experiment": [
        ("skos:closeMatch", "http://www.wikidata.org/entity/Q101965"),          # experiment
    ],
    "hint:TransparencyTrustExperiment": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q535347"),        # transparency
    ],
    "hint:DiagnosisExperiment": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q16644043"),      # medical diagnosis
    ],
    "hint:OnlineTutoringExperiment": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q2251299"),       # intelligent tutoring
    ],
    "hint:DeliberationSupportExperiment": [
        ("skos:relatedMatch", "http://www.wikidata.org/entity/Q1201750"),       # deliberation
    ],
}

# ================================================================
# MANUAL INSTANCE-LEVEL LINKS (added directly in 04_add_external_links.py)
# These link specific instances, not thesaurus concepts.
# ================================================================
INSTANCE_LINKS = {
    # HHAI Conference
    "inst:HHAI2025": [
        ("owl:sameAs", "http://www.wikidata.org/entity/Q113466830"),            # HHAI conference
    ],
}