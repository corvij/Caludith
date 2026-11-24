DECK = "OITE 2026::OITE 2026::1 Missed questions::ResStudy::Incorrect"

notes = [
    # (question id, Text, Back Extra)
    ("25FOOT-053",
     "Dancer with 1st MTP pain in grand plie (forefoot loaded, hallux maximally dorsiflexed), normal 1st MTP radiographs<br>"
     "Diagnosis: {{c1::FHL stenosing tenosynovitis (functional hallux rigidus)}}<br>"
     "Cause: {{c2::low-lying FHL muscle belly caught in the fibro-osseous tunnel}}<br>"
     "Treatment: {{c3::release the FHL fibro-osseous tunnel or debride the low-lying muscle belly}}",
     "Os trigonum causes posterior ankle impingement. Anterior ankle osteophytes cause anterior impingement. "
     "Cheilectomy is wrong because the 1st MTP joint has no arthritis. "
     "Peroneus brevis to longus transfer is not needed for a longitudinal tear and does not treat 1st MTP pain."),
    ("Foot22-008",
     "Isolated talonavicular arthrodesis<br>"
     "Hindfoot motion lost: {{c1::about 90%}}<br>"
     "Hindfoot motion remaining: {{c2::&lt;8% of preoperative motion}}",
     "The TN joint is the key joint of the hindfoot. Fusing it nearly eliminates subtalar and calcaneocuboid motion. "
     "Source for the &lt;8% figure: AAOS explanation (Astion et al, JBJS Am 1997)."),
    ("Foot20-040",
     "Chronic Achilles rupture, reconstruction by gap size<br>"
     "2 to 5 cm: {{c1::V-Y advancement}}, with or without {{c2::FHL augmentation}} if the gastrocsoleus is scarred or atrophic<br>"
     "More than 5 cm: {{c3::FHL tendon transfer}}",
     "Exam: cannot toe off, increased passive dorsiflexion, positive Thompson test, palpable gap. "
     "V-Y advancement avoids sacrificing a normal muscle-tendon unit. "
     "Peroneus brevis transfer can augment the Achilles but weakens eversion."),
    ("Foot22-032",
     "Hallux valgus surgery, sesamoid excision complications<br>"
     "Fibular (lateral) sesamoid excised: {{c1::hallux varus}}<br>"
     "Both sesamoids excised: {{c2::cock-up hallux}}",
     "Hallux valgus can coexist with pes planus, but surgery does not cause pes planus. "
     "Hallux rigidus is 1st MTP arthritis and is not linked to fibular sesamoid excision."),
    ("1046016",
     "Orthotic prescription by diagnosis<br>"
     "Metatarsalgia (ball of foot pain, worse barefoot on hard surfaces): {{c1::full-length insert with a metatarsal pad}}<br>"
     "Flexible flatfoot: {{c2::semi-rigid arch support with medial hindfoot posting}}<br>"
     "Flexible cavovarus: {{c3::lateral posting with 1st metatarsal head relief}}<br>"
     "UCBL orthosis: {{c4::controls the hindfoot}}",
     "The metatarsal pad shifts load off the metatarsal heads to a more proximal part of the foot."),
    ("25FOOT-097",
     "Diabetic plantar ulcer under a metatarsal head, nonsurgical treatment<br>"
     "Initial care: {{c1::debride devitalized tissue and offload}}<br>"
     "Offloading with fastest healing: {{c2::total contact cast}}<br>"
     "Why it beats a removable boot: {{c3::pressure reduction is similar, but a TCC cannot be taken off}}",
     "Aggressive acute glucose control has not been shown to change ulcer healing rate. "
     "A dynamic foot orthosis has a free-floating distal segment that reduces forefoot shear. It is used to prevent ulcers, not to heal them."),
    ("Foot20-055",
     "<img src=\"ResStudy_Foot20-055.png\"><br>"
     "Deep wound breakdown after total ankle replacement, by timing<br>"
     "Acute (3 weeks, tendon exposed): {{c1::return to OR, debride, exchange the polyethylene, flap coverage}}<br>"
     "Subacute (about 6 weeks) or chronic infection: {{c2::remove the implants and place an antibiotic spacer}}<br>"
     "Failed salvage or chronically infected TAR: {{c3::below-knee amputation}}",
     "A wound deep enough to expose tendon is assumed to reach the joint, so the poly is exchanged. "
     "Conversion to fusion is considered only when the wound bed is not infected. An intercalary allograft is wrong with active infection."),
]

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ankibuild import build

build(
    DECK, "foot_ankle_missed_2026-10-04", notes,
    tags=lambda qid: f"ResStudy Foot_Ankle ResStudy::{qid}",
    extra_suffix=lambda qid: f"Source: AAOS ResStudy #{qid}",
    # Text import only: these notes go into an existing deck and note type.
    apkg=False,
)
