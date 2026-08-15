"""
Static subject/topic catalogue for Class 12 (Intermediate 2nd Year)
MPC  -> Mathematics, Physics, Chemistry
BiPC -> Botany, Zoology, Physics, Chemistry

Topics below are indicative chapter names based on the standard AP/TS
Intermediate 2nd year syllabus. Feel free to edit / extend this file --
the app reads it fresh on every run, no other code needs to change.
"""

STREAMS = {
    "MPC": ["Mathematics", "Physics", "Chemistry"],
    "BiPC": ["Botany", "Zoology", "Physics", "Chemistry"],
}

# Subject -> icon (emoji) shown on tabs
SUBJECT_ICON = {
    "Mathematics": "📐",
    "Physics": "⚛️",
    "Chemistry": "🧪",
    "Botany": "🌿",
    "Zoology": "🐾",
}

TOPICS = {
    "Mathematics": [
        "Matrices",
        "Complex Numbers",
        "De Moivre's Theorem",
        "Quadratic Expressions",
        "Theory of Equations",
        "Permutations & Combinations",
        "Binomial Theorem",
        "Partial Fractions",
        "Measures of Dispersion",
        "Probability",
        "Random Variables & Probability Distributions",
        "Circle",
        "System of Circles",
        "Parabola",
        "Ellipse",
        "Hyperbola",
        "Three Dimensional Coordinates",
        "Direction Cosines & Direction Ratios",
        "Plane",
        "Limits & Continuity",
        "Differentiation",
        "Applications of Derivatives",
        "Integration",
        "Definite Integrals",
        "Differential Equations",
    ],
    "Physics": [
        "Waves",
        "Ray Optics and Optical Instruments",
        "Wave Optics",
        "Electric Charges and Fields",
        "Electrostatic Potential and Capacitance",
        "Current Electricity",
        "Moving Charges and Magnetism",
        "Magnetism and Matter",
        "Electromagnetic Induction",
        "Alternating Current",
        "Electromagnetic Waves",
        "Dual Nature of Radiation and Matter",
        "Atoms",
        "Nuclei",
        "Semiconductor Electronics",
        "Communication Systems",
    ],
    "Chemistry": [
        "Solid State",
        "Solutions",
        "Electrochemistry",
        "Chemical Kinetics",
        "Surface Chemistry",
        "General Principles of Metallurgy",
        "p-Block Elements (Group 15-18)",
        "d and f Block Elements",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids",
        "Organic Compounds Containing Nitrogen",
        "Biomolecules",
        "Polymers",
        "Chemistry in Everyday Life",
    ],
    "Botany": [
        "Reproduction in Organisms",
        "Sexual Reproduction in Flowering Plants",
        "Principles of Inheritance and Variation",
        "Molecular Basis of Inheritance",
        "Microbes in Human Welfare",
        "Biotechnology: Principles and Processes",
        "Biotechnology and its Applications",
        "Organisms and Populations",
        "Ecosystem",
        "Biodiversity and Conservation",
        "Plant Growth and Development",
    ],
    "Zoology": [
        "Human Reproduction",
        "Reproductive Health",
        "Evolution",
        "Human Health and Diseases",
        "Animal Husbandry",
        "Origin and Evolution of Life",
        "Applications of Biotechnology in Health",
        "Applications of Biotechnology in Agriculture",
        "Environmental Issues",
        "Locomotion and Movement (recap)",
        "Excretory Products and their Elimination (recap)",
    ],
}

DIFFICULTIES = ["Easy", "Medium", "Hard", "Mixed"]

QUESTION_COUNTS = [5, 10, 15, 20]
