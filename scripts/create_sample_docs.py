"""
scripts/create_sample_docs.py

One-time setup script: generates all 21 knowledge base documents used by
EcoGuide AI's RAG pipeline, organized into their category subfolders under data/.

Run this ONCE after cloning the project (or anytime you want to reset the
documents back to their original content).
"""

import os

# Resolve paths relative to the project root, not wherever this script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CATEGORIES = [
    "national_parks", "forest_reserves", "eco_hotels",
    "unesco", "wildlife_rules", "sustainable_tourism"
]

DOCUMENTS = {
    "national_parks/yala.txt": """Yala National Park
Yala is Sri Lanka's most visited national park, located in the southeast, spanning Block I through Block V.
It is famous for having one of the highest densities of leopards in the world. Other wildlife includes
elephants, sloth bears, crocodiles, and over 200 bird species. Best visited during the dry season from
February to July when animals gather near water sources. Block I is the most crowded; eco-conscious
travelers are encouraged to consider Block III or V for a quieter, lower-impact experience. Entry requires
a licensed jeep safari guide; self-driving inside the park is not permitted.""",

    "national_parks/wilpattu.txt": """Wilpattu National Park
Wilpattu is Sri Lanka's largest national park, known for its unique natural lakes ("villus") that attract
wildlife including leopards, sloth bears, and spotted deer. It is less crowded than Yala, making it a
better choice for travelers prioritizing sustainability and lower tourist density. The park was closed for
years during the civil conflict, allowing wildlife populations to recover undisturbed. Visitors should book
through registered eco-tour operators to ensure revenue supports park conservation.""",

    "national_parks/udawalawe.txt": """Udawalawe National Park
Udawalawe is best known for its large resident elephant population, visible year-round due to the
Udawalawe reservoir. It hosts the Elephant Transit Home, a rehabilitation center for orphaned elephant
calves, which is open to responsible visitors on a controlled viewing schedule. The park is a strong
choice for travelers interested in elephant conservation and shorter, lower-emission day trips from
Colombo or the southern coast.""",

    "national_parks/horton_plains.txt": """Horton Plains National Park
Located in the central highlands at high elevation, Horton Plains is known for its cloud forest, grasslands,
and the dramatic cliff formation called World's End. It is a UNESCO World Heritage Site component (Central
Highlands of Sri Lanka). Visitors must stay on marked trails to protect fragile montane ecosystems, and
early morning visits are recommended before cloud cover obscures the views.""",

    "forest_reserves/sinharaja.txt": """Sinharaja Forest Reserve
Sinharaja is Sri Lanka's last extensive area of primary tropical rainforest and a UNESCO World Heritage
Site. It hosts exceptional biodiversity with high rates of endemism among birds, amphibians, and plants.
Guided walks with certified local naturalist guides are required, both for visitor safety and to minimize
ecological disturbance. Sustainable tourism revenue here directly supports surrounding village conservation
programs.""",

    "forest_reserves/knuckles.txt": """Knuckles Mountain Range
The Knuckles Range is a rugged, biodiverse forest reserve in central Sri Lanka, part of the Central
Highlands UNESCO World Heritage Site. It offers multi-day trekking routes through cloud forest and
traditional villages. Because trails pass through fragile watershed areas, trekkers are strongly encouraged
to use registered local guides who follow leave-no-trace practices.""",

    "forest_reserves/kanneliya.txt": """Kanneliya Forest Reserve
Kanneliya is a rainforest reserve near Galle, part of the Kanneliya-Nakiyadeniya-Dediyagala (KDN) forest
complex, and a UNESCO Man and Biosphere Reserve. It is a good lower-impact alternative to Sinharaja for
travelers seeking rainforest biodiversity with fewer crowds and shorter travel distance from the south
coast.""",

    "eco_hotels/tea_trails.txt": """Tea Trails Bungalows
A collection of restored colonial-era tea planter bungalows in the hill country near Hatton, powered
partly by solar energy and supplied largely through local sourcing of food. Activities emphasize
low-impact experiences such as tea-plucking demonstrations and guided nature walks rather than
motorized excursions.""",

    "eco_hotels/kandalama.txt": """Heritance Kandalama
An eco-architecture hotel near Dambulla, built into a rock face and designed to blend into the
surrounding forest and lake landscape. It was among the first hotels in Sri Lanka to pursue
Green Globe certification, with programs for water recycling, waste segregation, and community
employment from nearby villages.""",

    "eco_hotels/jetwing_vil_uyana.txt": """Jetwing Vil Uyana
Located near Sigiriya, this property is built around restored wetland, forest, and paddy habitats,
designed to attract native birdlife directly into guest view. It follows a model of habitat restoration
combined with low-density room placement to minimize ecological footprint per guest.""",

    "eco_hotels/rainforest_ecolodge.txt": """Rainforest Ecolodge, Sinharaja
A small-scale lodge bordering Sinharaja Forest Reserve, built with local materials and run with strong
community-employment ties to nearby villages. It emphasizes guided rainforest walks over passive
tourism, directing a portion of proceeds toward reserve conservation.""",

    "unesco/sinharaja_whs.txt": """UNESCO Site: Sinharaja Forest Reserve
Inscribed as a UNESCO World Heritage Site for its outstanding biodiversity and status as one of the
last viable areas of primary rainforest in Sri Lanka. Protection status restricts development and
requires licensed guiding for all visitor access.""",

    "unesco/central_highlands.txt": """UNESCO Site: Central Highlands of Sri Lanka
This UNESCO World Heritage Site combines the Peak Wilderness Protected Area, Horton Plains National
Park, and the Knuckles Conservation Forest. It is recognized for exceptional biodiversity, including
many endemic species found nowhere else, and for globally significant montane cloud forest ecosystems.""",

    "unesco/galle_fort.txt": """UNESCO Site: Old Town of Galle and its Fortifications
A fortified city founded by Portuguese colonizers and extensively developed by the Dutch in the 17th
century, recognized as an outstanding example of a fortified colonial city blending European
architecture with South Asian traditions. Sustainable tourism guidance encourages visitors to support
local heritage-preservation businesses within the fort walls.""",

    "wildlife_rules/park_etiquette.txt": """General Wildlife Park Rules in Sri Lanka
Visitors must remain inside vehicles in most national parks except at designated points. Feeding
wildlife is strictly prohibited. Vehicles must maintain a minimum safe distance from elephants and
leopards, and jeep drivers are required to follow park-specified speed limits. Playing loud music,
littering, and off-trail walking are prohibited in all national parks and reserves.""",

    "wildlife_rules/elephant_safety.txt": """Elephant Encounter Safety Guidelines
Sri Lanka has one of the highest human-elephant conflict rates in the world outside protected areas.
Within parks, visitors should never approach elephants on foot, and vehicles should not block an
elephant's path of movement. Musth (a periodic aggressive state in male elephants) requires an even
greater safety distance, and guides are trained to recognize its signs.""",

    "wildlife_rules/marine_protection.txt": """Marine Wildlife Protection Rules
Sri Lanka's coastal waters host whale and dolphin watching, particularly off Mirissa and Trincomalee.
Regulations restrict how closely boats may approach marine mammals and cap the number of boats
allowed near a sighting simultaneously, to reduce stress on the animals. Certified operators follow
distance and speed limits set by Sri Lanka's Department of Wildlife Conservation.""",

    "sustainable_tourism/carbon_conscious_travel.txt": """Carbon-Conscious Travel in Sri Lanka
Sustainable itineraries favor train travel (such as the scenic Kandy-to-Ella route) over domestic
flights, and group multiple nearby attractions to reduce transit distance. Choosing accommodations
with verified sustainability certifications and staying longer in fewer locations both reduce a
trip's overall carbon footprint.""",

    "sustainable_tourism/community_based_tourism.txt": """Community-Based Tourism Initiatives
Several Sri Lankan villages near reserves, including areas bordering Sinharaja and Knuckles, run
community-based tourism programs where a portion of tourist spending funds local schools, healthcare,
or reserve patrols. Choosing homestays and community-guided treks over large hotel chains directs
more revenue directly to local conservation stakeholders.""",

    "sustainable_tourism/plastic_reduction.txt": """Plastic Reduction Guidelines for Travelers
Many eco-lodges and national parks in Sri Lanka now discourage single-use plastic bottles, encouraging
refillable water bottle stations instead. Travelers are advised to carry reusable bottles and bags,
particularly in coastal and marine park areas where plastic waste directly threatens marine wildlife.""",

    "sustainable_tourism/responsible_trekking.txt": """Responsible Trekking Practices
Leave-no-trace principles apply throughout Sri Lanka's forest reserves: pack out all waste, stay on
marked trails to prevent soil erosion in fragile highland ecosystems, and avoid picking plants or
disturbing wildlife habitats. Licensed local guides are strongly recommended both for safety and to
ensure trekking revenue benefits conservation-linked communities.""",
}


def create_documents():
    """Creates category folders (if missing) and writes all 21 document files."""

    # Ensure every category folder exists
    for category in CATEGORIES:
        os.makedirs(os.path.join(DATA_DIR, category), exist_ok=True)

    # Write each document to its correct category subfolder
    created_count = 0
    for relative_path, content in DOCUMENTS.items():
        full_path = os.path.join(DATA_DIR, relative_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        created_count += 1
        print(f"  ✓ {relative_path}")

    print(f"\n✅ Created {created_count} documents across {len(CATEGORIES)} categories")
    print(f"   Location: {DATA_DIR}")


if __name__ == "__main__":
    create_documents()