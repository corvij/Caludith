import re, sys, os

# Case prep deck for two shoulder cases with Dr. Galatz (arthroscopic rotator cuff
# repair of a large posterosuperior tear, and conversion of an anatomic TSA to a
# reverse). Emphasis on anatomy, structures at risk, and distances. No patient data.

DECK = "OITE 2026::OITE 2026::2 Case prep::Galatz shoulder"
BASENAME = "galatz_shoulder_2026-10-25"

notes = [
    # (tag group, Text, Back Extra)

    # ---------- Axillary nerve ----------
    ("Anatomy::Axillary_nerve",
     "Axillary nerve origin and course<br>"
     "Roots: {{c1::C5, C6}} from the {{c1::posterior cord}}<br>"
     "Leaves the cord at the level of the {{c2::coracoid}}, behind the {{c2::axillary artery}}<br>"
     "Passes under the inferior border of the {{c3::subscapularis}}, hugs the {{c3::inferior capsule}}<br>"
     "Exits through the {{c4::quadrilateral space}} with the {{c4::posterior humeral circumflex artery}}",
     "Anterior branch: anterior and middle deltoid. Posterior branch: teres minor, posterior deltoid, superior lateral brachial cutaneous nerve."),
    ("Anatomy::Axillary_nerve",
     "Quadrilateral space borders and contents<br>"
     "Superior: {{c1::teres minor}}<br>Inferior: {{c1::teres major}}<br>"
     "Medial: {{c2::long head of triceps}}<br>Lateral: {{c2::humeral shaft}}<br>"
     "Contents: {{c3::axillary nerve and posterior humeral circumflex artery}}",
     "Triangular interval (below teres major, between long head and shaft): radial nerve and profunda brachii. "
     "Triangular space (above teres major, medial to long head): circumflex scapular artery."),
    ("Anatomy::Axillary_nerve",
     "Axillary nerve distances<br>"
     "Below the lateral edge of the acromion on the deep deltoid: {{c1::5 to 7 cm, mean about 6 cm, as short as 3 cm}}<br>"
     "From the inferior glenoid rim at 6 o'clock: {{c2::10 to 12 mm}}<br>"
     "From the inferior border of the subscapularis at the musculotendinous junction: {{c3::3 to 5 mm}}",
     "Lateral arthroscopic portals and the deltoid split stay within 3 to 4 cm of the acromion. "
     "The 6 o'clock position is the closest point of the whole nerve course to the joint."),
    ("Anatomy::Axillary_nerve",
     "Tug test for the axillary nerve (Flatow and Bigliani 1992)<br>"
     "One finger along the {{c1::anterior surface of the subscapularis, below the coracoid}}<br>"
     "Other finger on the {{c1::deep surface of the deltoid posteriorly}}<br>"
     "A tug on one is felt by the other because {{c2::both are on the same axillary nerve}}",
     "Do it before the subscapularis is taken down in any open shoulder, and again in a revision where scar fixes the nerve to the capsule."),
    ("Anatomy::Axillary_nerve",
     "Steps of a deltopectoral revision arthroplasty where the axillary nerve is injured<br>"
     "{{c1::Subscapularis takedown carried too far inferior}}<br>"
     "{{c2::Inferior capsular release off the humeral neck or the glenoid}}<br>"
     "{{c3::Inferior blade of the Fukuda or the inferior glenoid retractor}}<br>"
     "{{c4::Inferior baseplate screw aimed anteriorly}}<br>"
     "{{c5::Traction from overlengthening the arm}}",
     "Protect it: find and palpate it first, release the inferior capsule on the humeral side with the arm externally rotated and a retractor between nerve and capsule, keep retractors on bone."),
    ("Anatomy::Axillary_nerve",
     "Steps of arthroscopic cuff repair where the axillary nerve is at risk<br>"
     "{{c1::Lateral or anterolateral portal placed more than 4 to 5 cm below the acromion}}<br>"
     "{{c2::Inferior capsular release or a 6 o'clock anchor}}<br>"
     "{{c3::Posterior portal placed too inferior, into the quadrilateral space}}",
     "Standard posterior portal: 2 cm inferior and 1 to 2 cm medial to the posterolateral acromion corner."),

    # ---------- Suprascapular nerve ----------
    ("Anatomy::Suprascapular_nerve",
     "Suprascapular nerve course<br>"
     "Origin: {{c1::upper trunk (C5, C6) at Erb's point}}<br>"
     "Enters the scapula through the {{c2::suprascapular notch}} beneath the {{c2::transverse scapular ligament}}; the artery goes {{c3::over the ligament}}<br>"
     "Motor branches to {{c4::supraspinatus}}, then around the {{c5::spinoglenoid notch}} under the spinoglenoid ligament to {{c5::infraspinatus}}",
     "Army over Navy: artery over the ligament, nerve under it. Also gives sensory branches to the glenohumeral and AC joints."),
    ("Anatomy::Suprascapular_nerve",
     "Suprascapular nerve distances (Bigliani 1990)<br>"
     "Supraglenoid tubercle to the suprascapular notch: {{c1::about 3 cm}}<br>"
     "Posterior glenoid rim to the nerve at the spinoglenoid notch: {{c2::about 1.8 to 2 cm}}<br>"
     "Lateral advancement of a retracted supraspinatus that tensions the nerve (Warner 1992): {{c3::more than 3 cm}}",
     "Medial dissection more than 1 to 1.5 cm medial to the glenoid rim along the supraspinatus or infraspinatus approaches the nerve. "
     "Releases for a retracted cuff stop at the glenoid rim."),
    ("Anatomy::Suprascapular_nerve",
     "Reverse baseplate screws that reach the suprascapular nerve<br>"
     "{{c1::Posterior}} screw exits at the {{c1::spinoglenoid notch}}, about 2 cm medial to the posterior rim<br>"
     "{{c2::Superior}} screw exits at the {{c2::suprascapular notch}}, about 3 cm medial to the superior rim<br>"
     "Safe targets: superior screw into the {{c3::coracoid base}}, inferior screw into the {{c3::lateral pillar}}",
     "Keep posterior and superior screws short (about 2 cm or less). The inferior and superior pillar screws are what hold a revision baseplate."),
    ("Anatomy::Suprascapular_nerve",
     "Isolated infraspinatus atrophy with normal supraspinatus, in a thrower or with a paralabral cyst<br>"
     "Site of compression: {{c1::spinoglenoid notch}}<br>"
     "Both supraspinatus and infraspinatus weak: {{c2::suprascapular notch}}",
     "A spinoglenoid cyst usually comes from a posterosuperior labral tear. Decompress the cyst and repair the labrum."),

    # ---------- Musculocutaneous, plexus, radial ----------
    ("Anatomy::Musculocutaneous",
     "Musculocutaneous nerve in the deltopectoral approach<br>"
     "Enters the {{c1::coracobrachialis}} from its medial side {{c2::3 to 8 cm below the coracoid tip, mean about 5.6 cm}}, as close as {{c2::1.5 cm}}<br>"
     "Injured by {{c3::retractors placed medial to or under the conjoined tendon}}<br>"
     "Deficit: {{c4::weak elbow flexion and numb lateral forearm}}",
     "Stay lateral to the conjoined tendon. Rest retractors on bone, not on the tendon. The same nerve is at risk in an open subpectoral biceps tenodesis."),
    ("Anatomy::Plexus",
     "The coracoid as the lighthouse of the shoulder<br>"
     "Medial and inferior to the coracoid, deep to the pectoralis minor: {{c1::axillary artery and brachial plexus}}<br>"
     "Lateral to the coracoid: {{c2::safe}}<br>"
     "Cords are named by their position relative to the {{c3::second part of the axillary artery, behind the pectoralis minor}}",
     "Attachments: conjoined tendon at the tip, pectoralis minor medially, coracoacromial ligament laterally, coracohumeral ligament laterally toward the tuberosities, coracoclavicular ligaments superiorly."),
    ("Anatomy::Plexus",
     "Arm lengthening in reverse shoulder arthroplasty<br>"
     "Lengthening associated with brachial plexus stretch (Ladermann): {{c1::more than about 2.5 cm}}<br>"
     "First nerve to show a traction neurapraxia: {{c2::ulnar}}<br>"
     "Intraoperative tension checks: {{c3::conjoined tendon tension, 1 to 2 mm shuck, stable in extension and external rotation}}",
     "Most traction neurapraxias after reverse arthroplasty recover."),
    ("Anatomy::Radial_nerve",
     "Radial nerve during humeral stem extraction or a humeral window<br>"
     "Spiral groove: from about {{c1::20 cm above the medial epicondyle}} to {{c1::10 cm above the lateral epicondyle}}<br>"
     "Crosses the lateral intermuscular septum about {{c2::10 cm above the lateral epicondyle}}<br>"
     "Deltoid tuberosity, the distal limit of a safe anterolateral window: about {{c3::15 cm below the acromion}}<br>"
     "Cerclage wires are passed {{c4::subperiosteally}}",
     "Have cables and a long revision stem available whenever a stem might come out."),

    # ---------- Interscalene block ----------
    ("Anesthesia::Block",
     "Interscalene block anatomy and complications<br>"
     "Roots blocked: {{c1::C5 to C7}} between the {{c1::anterior and middle scalene}} at the level of the cricoid (C6)<br>"
     "Nerve on the anterior scalene blocked almost every time: {{c2::phrenic}}<br>"
     "Horner syndrome from the {{c3::stellate ganglion}}; hoarseness from the {{c3::recurrent laryngeal nerve}}<br>"
     "Nerves that pierce the middle scalene: {{c4::dorsal scapular and long thoracic}}",
     "Other risks: pneumothorax, vertebral artery or intrathecal injection, nerve injury. Ask about lung disease before a block that paralyzes a hemidiaphragm."),
    ("Anesthesia::Positioning",
     "Beach chair position hazards<br>"
     "Reflex causing sudden bradycardia and hypotension: {{c1::Bezold Jarisch}}, more common with interscalene block and epinephrine<br>"
     "Cerebral perfusion: an arm cuff reads {{c2::higher than the pressure at the brain}}; correct by about {{c2::0.77 mmHg per cm}} between cuff and external auditory meatus<br>"
     "Lateral decubitus hazard instead: {{c3::brachial plexus traction}}",
     "Keep mean arterial pressure at brain level above about 70. Cerebral oximetry is an option."),

    # ---------- Vessels ----------
    ("Anatomy::Vessels",
     "Cephalic vein in the deltopectoral approach<br>"
     "Retract it {{c1::laterally with the deltoid}} because {{c1::more tributaries come from the deltoid side}}<br>"
     "Artery crossing the top of the groove: {{c2::deltoid branch of the thoracoacromial artery}}<br>"
     "In a revision, find the virgin plane {{c3::proximally at the clavicle}}",
     ""),
    ("Anatomy::Vessels",
     "The three sisters<br>"
     "Vessels: {{c1::anterior humeral circumflex artery and its two venae comitantes}}<br>"
     "Location: {{c2::along the inferior border of the subscapularis, running to the bicipital groove}}<br>"
     "Ascending branch into the humeral head: {{c3::arcuate artery}}",
     "Cauterize or ligate before the subscapularis comes down. Scarred and bleeding in a revision."),
    ("Anatomy::Vessels",
     "Humeral head blood supply<br>"
     "Historically credited vessel: {{c1::anterior humeral circumflex (arcuate artery)}}<br>"
     "Vessel shown by Hettrich 2010 to supply about 64% of the head: {{c2::posterior humeral circumflex}}<br>"
     "The posterior humeral circumflex runs with the {{c3::axillary nerve through the quadrilateral space}}",
     "Explains why many four part fractures with an intact medial hinge keep a viable head."),
    ("Anatomy::Vessels",
     "Bleeders by step<br>"
     "Anterior acromion and coracoacromial ligament during acromioplasty: {{c1::acromial branch of the thoracoacromial artery}}<br>"
     "Transverse scapular ligament during medial cuff dissection: {{c2::suprascapular artery}}<br>"
     "Lateral scapular border during posterior and inferior glenoid exposure: {{c3::circumflex scapular artery}}",
     "Cauterize before cutting the CA ligament."),

    # ---------- Arthroscopic portals and intervals ----------
    ("RCR::Portals",
     "Arthroscopic shoulder portals and the structure nearest each<br>"
     "Posterior portal: {{c1::2 cm inferior and 1 to 2 cm medial to the posterolateral acromion corner}}; nearest structures {{c2::suprascapular nerve 2 cm medial, axillary nerve inferior}}<br>"
     "Anterior portal: {{c3::through the rotator interval, lateral to the coracoid}}; nearest structures {{c4::cephalic vein and musculocutaneous nerve if medial}}<br>"
     "Lateral portal: {{c5::2 to 4 cm below the lateral acromion, in line with the posterior clavicle}}; nearest structure {{c6::axillary nerve at 5 to 7 cm}}",
     "Neviaser portal (supraclavicular fossa) passes through trapezius and supraspinatus with the suprascapular nerve and artery 2.5 to 3 cm medial."),
    ("RCR::Anatomy",
     "Rotator interval<br>"
     "Superior border: {{c1::supraspinatus}}<br>Inferior border: {{c1::subscapularis}}<br>"
     "Medial: {{c2::coracoid base}}<br>Lateral: {{c2::transverse humeral ligament}}<br>"
     "Contents: {{c3::coracohumeral ligament, superior glenohumeral ligament, long head of biceps, capsule}}",
     "The SGHL and CHL form the medial sling that stabilizes the biceps at the groove entrance."),
    ("RCR::Anatomy",
     "Subacromial bursa boundaries<br>"
     "Roof: {{c1::coracoacromial arch}}<br>Floor: {{c1::rotator cuff}}<br>"
     "Medial: {{c2::coracoid}}<br>Lateral: {{c2::deltoid}}",
     "Bursectomy with the shaver facing away from the cuff."),

    # ---------- Cuff footprint, cable, vascularity ----------
    ("RCR::Footprint",
     "Greater tuberosity facets and insertions<br>"
     "Superior facet: {{c1::supraspinatus}}<br>Middle facet: {{c1::infraspinatus}}, which wraps {{c2::anteriorly over the anterolateral tuberosity}}<br>"
     "Inferior facet: {{c3::teres minor}}<br>"
     "Lesser tuberosity: {{c4::subscapularis}}, upper {{c4::60%}} tendon and lower {{c4::40%}} muscle",
     "Mochizuki 2008 showed the supraspinatus footprint is small and the infraspinatus is large, so most large 'supraspinatus' tears are two tendon tears."),
    ("RCR::Footprint",
     "Supraspinatus footprint size<br>"
     "Mochizuki 2008: about {{c1::7 mm medial to lateral, 13 mm anterior to posterior}}<br>"
     "Older combined figures (Dugas 2002): about {{c2::23 mm anterior to posterior, 13 to 16 mm medial to lateral}}<br>"
     "Best tuberosity bone for anchors: {{c3::anteromedial, near the articular margin}}; worst: {{c3::posterolateral in older patients}}",
     "Prepare the footprint to bleeding bone without decorticating, so anchors still hold."),
    ("RCR::Anatomy",
     "Rotator cable and crescent (Burkhart)<br>"
     "Cable: thickening of the {{c1::coracohumeral ligament}} running from the {{c1::anterior supraspinatus to the inferior infraspinatus}}<br>"
     "Dimensions: about {{c2::12 mm wide, 4 cm long}}<br>"
     "Crescent: {{c3::thin tissue lateral to the cable}}<br>"
     "Why a crescent tear with an intact cable can elevate: {{c4::suspension bridge, load transferred along the cable}}",
     "Suture passes should capture the cable, 10 to 12 mm medial to the tendon edge."),
    ("RCR::Anatomy",
     "Critical zone of the rotator cuff<br>"
     "Location: about {{c1::1 cm from the insertion of the supraspinatus}}<br>"
     "Why it fails: {{c2::hypovascular watershed between the suprascapular and humeral circumflex supply}}",
     "Codman's term."),
    ("RCR::Healing",
     "Tendon to bone healing after cuff repair<br>"
     "Native enthesis zones: {{c1::tendon, uncalcified fibrocartilage, calcified fibrocartilage, bone}}<br>"
     "Repaired tendon heals by {{c2::fibrovascular scar}}, not regeneration of the enthesis, so it is {{c2::mechanically weaker}}<br>"
     "Drug class shown in rat models to impair tendon to bone healing (Cohen 2006, Galatz lab): {{c3::NSAIDs (COX inhibitors)}}",
     "Practical answer: no NSAIDs in the early healing window after a cuff repair; acetaminophen, the block catheter, ice."),

    # ---------- Acromion, CA ligament, distal clavicle ----------
    ("RCR::Acromion",
     "Bigliani acromion types and the coracoacromial ligament in a large tear<br>"
     "Type 1 {{c1::flat}}, type 2 {{c1::curved}}, type 3 {{c1::hooked}}<br>"
     "In a large or massive tear release the CA ligament only {{c2::partially}} because it is the last restraint to {{c2::anterosuperior escape}}<br>"
     "Over resection of the acromion detaches the {{c3::deltoid origin}}",
     "Acromioplasty with repair shows no clinical difference in trials; spurs that abrade the cuff are still smoothed. Look for an os acromiale on the axillary view."),
    ("RCR::AC_joint",
     "Distal clavicle excision limits<br>"
     "Resect less than {{c1::1 cm}} to keep the {{c1::superior and posterior AC ligaments}}<br>"
     "Trapezoid inserts {{c2::2.5 cm}} and conoid {{c2::4.5 cm}} from the distal end",
     ""),

    # ---------- Cuff classification and imaging ----------
    ("RCR::Classification",
     "Rotator cuff tear size and shape<br>"
     "Cofield: small {{c1::under 1 cm}}, medium {{c1::1 to 3 cm}}, large {{c1::3 to 5 cm}}, massive {{c1::over 5 cm}}; Gerber massive: {{c1::two or more complete tendons}}<br>"
     "Burkhart shapes: {{c2::crescent}} repairs direct to bone; {{c2::U shaped}} needs margin convergence first; {{c2::L and reverse L}} have one mobile limb; massive contracted needs releases",
     "Patte retraction: 1 near the insertion, 2 at the humeral head, 3 at the glenoid."),
    ("RCR::Imaging",
     "Muscle quality on MRI<br>"
     "Goutallier: 0 normal, 1 streaks, 2 {{c1::more muscle than fat}}, 3 {{c1::equal}}, 4 {{c1::more fat than muscle}}; stage {{c2::2 or higher}} predicts non healing<br>"
     "Tangent sign (Zanetti): line from the {{c3::superior coracoid to the superior scapular spine}} on the sagittal oblique; positive when the {{c3::supraspinatus belly does not cross it}}<br>"
     "Acromiohumeral interval suggesting an irreparable tear: {{c4::under 7 mm}}",
     "Sugaya types IV and V on postoperative MRI are re-tears."),
    ("RCR::Outcomes",
     "Predictors of non healing after rotator cuff repair<br>"
     "Patient: {{c1::age over 65, smoking, diabetes, osteoporosis}}<br>"
     "Tear: {{c2::size over 3 cm, two tendons, Patte 2 or 3, Goutallier 2 or more, positive tangent sign}}<br>"
     "Technique: {{c3::poor footprint prep, over tension, medial row cutout, over tightened lateral row causing type 2 failure at the musculotendinous junction}}",
     "Boileau 2005: age was the strongest predictor. Clinical satisfaction runs higher than the structural healing rate."),
    ("RCR::Outcomes",
     "Galatz 2004 JBJS, arthroscopic repair of large and massive tears<br>"
     "Recurrent defect on ultrasound at 1 year: {{c1::17 of 18}}<br>"
     "Clinical result: {{c2::pain and function improved substantially at 1 year, then declined somewhat by 2 years}}<br>"
     "Lesson: {{c3::clinical success and structural healing are separate questions}}",
     "Healed repairs give better strength and durability. Know this one cold with her."),
    ("RCR::Technique",
     "Arthroscopic repair technique facts<br>"
     "Deadman angle: {{c1::45 degrees or less}} so bone resists the pull<br>"
     "Double row versus single row in tears over 3 cm: {{c2::better structural healing, no consistent clinical difference}}<br>"
     "Early versus delayed motion in large tears (Cuff and Pupello 2012): {{c3::delayed motion had better healing}}<br>"
     "Pump pressure: {{c4::40 to 60 mmHg}} with epinephrine; keep the systolic to pump gradient under about {{c4::49 mmHg}}",
     "Medial row at the articular margin, lateral row 5 to 10 mm below the lateral tuberosity edge."),
    ("RCR::Complications",
     "Complications after arthroscopic cuff repair<br>"
     "Most common: {{c1::stiffness}}<br>"
     "Most common structural failure: {{c2::re-tear}}<br>"
     "Infection organism in men: {{c3::Cutibacterium acnes}}<br>"
     "Type 2 failure: {{c4::medial to the medial row at the musculotendinous junction}}",
     "Stiffness after repair usually resolves with time and therapy. A re-tear does not."),
    ("RCR::Alternatives",
     "Indications for reverse over repair in a cuff tear<br>"
     "{{c1::Cuff tear arthropathy}}<br>"
     "{{c2::Pseudoparalysis with an irreparable tear}}<br>"
     "{{c3::Failed prior repair in an older, lower demand patient}}<br>"
     "Not indicated when: {{c4::no arthritis, elevation preserved, subscapularis intact, patient wants strength for sport}}",
     "Age alone is not a contraindication to repair."),

    # ---------- Deltopectoral approach ----------
    ("TSA::Approach",
     "Deltopectoral approach, structure by layer<br>"
     "Interval: {{c1::deltoid (axillary nerve) and pectoralis major (medial and lateral pectoral nerves)}}<br>"
     "Vein in the groove: {{c2::cephalic}}, taken {{c2::laterally}}<br>"
     "Conjoined tendon: {{c3::short head of biceps and coracobrachialis}} from the {{c3::coracoid tip}}<br>"
     "Landmark for the inferior limit of the humeral head: {{c4::upper border of the pectoralis major, 5.6 cm below the top of the head}}",
     "Release the upper 1 cm of the pectoralis major insertion only if more exposure is needed."),
    ("TSA::Approach",
     "Subcoracoid release in an open shoulder<br>"
     "Ligament incised from the coracoid base: {{c1::coracohumeral}}<br>"
     "Spaces cleared of adhesions for retractors: {{c2::subcoracoid, subacromial, subdeltoid}}<br>"
     "Nerve palpated at the end of this step: {{c3::axillary, below the subscapularis}}",
     "In a revision the nerve may be scarred to the capsule. Find it before anything is cut."),
    ("TSA::Approach",
     "Inferior capsular release off the humeral neck<br>"
     "Nerve on the capsule: {{c1::axillary}}<br>"
     "Arm position that lets the nerve fall away: {{c2::external rotation with adduction}}<br>"
     "Protection: {{c3::blunt retractor between nerve and capsule, cautery pointed at bone}}<br>"
     "Forcing dislocation of a stiff revision shoulder risks: {{c4::humeral shaft fracture}}",
     "Dislocate with extension, adduction, external rotation. Release more before forcing it."),
    ("TSA::Approach",
     "Glenoid retractors and the structure under each<br>"
     "Fukuda on the humerus: inferior blade near the {{c1::axillary nerve}}, posterior blade near the {{c1::posterior circumflex vessels}}<br>"
     "Anterior two prong on the glenoid neck: {{c2::subscapularis with the axillary nerve under it}}<br>"
     "Superior Hohmann: {{c3::supraspinatus, biceps stump, suprascapular nerve 3 cm medial}}<br>"
     "Inferior retractor: {{c4::axillary nerve about 1 cm away}}",
     "Retractors sit on bone under direct vision. The circumferential capsular release for glenoid exposure is where most axillary injuries happen in revision."),

    # ---------- Glenoid and baseplate ----------
    ("TSA::Glenoid",
     "Glenoid vault anatomy for a baseplate<br>"
     "Vault depth at the center line: about {{c1::25 to 30 mm}}, thinner {{c1::anteriorly and inferiorly}}<br>"
     "Medial perforation enters the {{c2::subscapularis fossa}}; not dangerous, but it costs {{c2::fixation}}<br>"
     "Central post aimed down the {{c3::glenoid center line toward the lateral pillar}}",
     "Walch glenoid: A1, A2 centered; B1 posterior subluxation without biconcavity; B2 biconcave; B3 monoconcave with retroversion over 15; C dysplastic retroversion over 25."),
    ("TSA::Glenoid",
     "Reverse baseplate position<br>"
     "Height: {{c1::inferior on the glenoid face}} with glenosphere overhang of {{c1::2 to 4 mm}}<br>"
     "Tilt: {{c2::neutral to slight inferior, never superior}}<br>"
     "Why superior tilt is bad: {{c3::baseplate loosening and notching}}",
     "Inferior overhang limits scapular notching (Sirveaux grades 1 to 4; grade 4 extends under the baseplate)."),
    ("TSA::Glenoid",
     "Revision glenoid bone loss (Antuna)<br>"
     "Types: {{c1::central, peripheral, combined}}, each {{c1::mild, moderate, severe}}<br>"
     "Options when the central post has no native bone: {{c2::long post baseplate, augmented baseplate, femoral head or iliac crest graft with a long post, or staged grafting}}",
     "A hybrid glenoid with a trabecular metal central post leaves a central cavitary defect after removal."),
    ("TSA::Glenoid",
     "Removing a hybrid pegged glenoid with a trabecular metal central post<br>"
     "Step 1: {{c1::separate the polyethylene from the pegs with an osteotome or saw through the poly}}<br>"
     "Step 2: {{c2::remove the cemented peripheral pegs and curette the cement}}<br>"
     "Step 3: {{c3::trephine or burr out the ingrown central post with as little bone loss as possible}}<br>"
     "Then: {{c4::classify the defect and choose the baseplate}}",
     "Every instrument aims medially at the vault. The suprascapular nerve is superior and posterior, 2 to 3 cm medial to the rim."),

    # ---------- Failure of anatomic TSA ----------
    ("TSA::Failure",
     "Modes of failure of anatomic total shoulder arthroplasty<br>"
     "Most common long term: {{c1::glenoid loosening}}<br>"
     "Most common reason for conversion to reverse in the first few years: {{c2::rotator cuff failure}}<br>"
     "Early cuff failure is usually {{c3::subscapularis}}; late is {{c3::posterosuperior (supraspinatus)}}<br>"
     "Others: {{c4::instability, infection, stiffness, periprosthetic fracture, humeral loosening (rare)}}",
     ""),
    ("TSA::Failure",
     "Secondary rotator cuff dysfunction after anatomic TSA (Young, Walch 2012)<br>"
     "Incidence at 10 years: {{c1::about 17%}}<br>"
     "Radiographic sign: {{c2::proximal migration of the head on the true AP}}<br>"
     "Consequence for the glenoid: {{c3::rocking horse loosening from eccentric superior loading}}<br>"
     "Preoperative risk factor: {{c4::infraspinatus fatty infiltration}}",
     "Head centered on the axillary with migration on the Grashey means the posterior cuff is working and the superior cuff is not."),
    ("TSA::Failure",
     "Subscapularis after anatomic TSA<br>"
     "Lapner RCT, peel versus lesser tuberosity osteotomy: {{c1::no difference in outcomes}}<br>"
     "Miller 2003: most patients after tenotomy repair had {{c2::an abnormal belly press or lift off}}<br>"
     "Factors that overload the repair: {{c3::overstuffing with a thick head, anterior head placement, a stiff shoulder needing a large anterior release}}<br>"
     "Exam of a failed subscap: {{c4::positive belly press and lift off, internal rotation lag, anterior subluxation on the axillary}}",
     ""),
    ("TSA::Failure",
     "Exam findings that localize a cuff failure after arthroplasty<br>"
     "Positive belly press, negative ER lag, negative hornblower, head centered on the axillary: {{c1::subscapularis weak, posterior cuff intact}}<br>"
     "Head riding on the acromion on the Grashey with weak supraspinatus: {{c2::posterosuperior insufficiency with superior migration}}<br>"
     "Active elevation preserved above 90: {{c3::not pseudoparalytic}}",
     "A reverse in a non pseudoparalytic patient treats pain, popping, and glenoid protection; it does not add much elevation."),
    ("TSA::Infection",
     "Infection workup of a painful shoulder arthroplasty<br>"
     "Organism: {{c1::Cutibacterium acnes}}, more in {{c1::men}}<br>"
     "ESR and CRP: {{c2::often normal, insensitive}}<br>"
     "Standard: {{c3::3 to 5 intraoperative tissue cultures held 14 days}}<br>"
     "Unexpected positive cultures at revision: {{c4::15 to 30%}}",
     "2018 International Consensus Meeting shoulder PJI definitions: definite, probable, possible, unlikely. Ask whether the attending holds antibiotics until cultures are taken."),

    # ---------- Reverse principles and complications ----------
    ("RSA::Principles",
     "Grammont principles of the reverse shoulder<br>"
     "{{c1::Medialize the center of rotation}}<br>"
     "{{c2::Distalize the humerus to tension the deltoid}}<br>"
     "{{c3::Semi constrained articulation gives a fixed fulcrum}}<br>"
     "Net effect: {{c4::larger deltoid moment arm and more deltoid fibers recruited as elevators}}",
     "Lateralization (glenoid or humeral side) reduces notching, restores deltoid contour, improves external rotation, and raises baseplate shear."),
    ("RSA::Principles",
     "Requirements and contraindications for a reverse<br>"
     "Must have: {{c1::working deltoid and axillary nerve}}, {{c2::no active infection}}, {{c3::enough glenoid bone to fix a baseplate}}<br>"
     "Platform stem conversion versus full humeral revision (Wagner 2016): {{c4::shorter OR time, less blood loss, fewer humeral complications}}",
     "Confirm deltoid contraction in all three heads and lateral shoulder sensation before any reverse."),
    ("RSA::Complications",
     "Complications of revision reverse shoulder arthroplasty<br>"
     "Most common: {{c1::instability}}, about {{c1::8 to 15%}} in older revision series<br>"
     "Causes of instability: {{c2::insufficient deltoid tension, loss of the subscapularis, impingement, component malposition}}<br>"
     "Stress fracture sites: {{c3::acromion and scapular spine (Levy types I to III)}}<br>"
     "Stress riser for a spine fracture: {{c4::superior baseplate screw into the spine base}}",
     "Scapular notching: Sirveaux 1 to 4. Nerve injury: axillary during release, plexus from lengthening. Hematoma is more likely in an anticoagulated patient."),
    ("RSA::Technique",
     "Judging tension and stability in a reverse<br>"
     "Conjoined tendon: {{c1::taut}}<br>"
     "Shuck: {{c2::1 to 2 mm of distraction}}<br>"
     "Stability tested in: {{c3::extension, adduction, and external rotation}}<br>"
     "Impingement checked in: {{c4::adduction against the scapular neck}}",
     "Lengthening under about 2.5 cm to protect the plexus."),
    ("Anatomy::Humerus",
     "Humeral landmarks for arthroplasty<br>"
     "Normal head retroversion: {{c1::20 to 30 degrees}} relative to the transepicondylar axis<br>"
     "Landmark for version: {{c2::bicipital groove}}; stem fin sits about {{c2::9 mm posterior to the groove}} in fracture cases<br>"
     "Deltoid insertion: {{c3::deltoid tuberosity, about 15 cm below the acromion}}",
     ""),
    ("Anatomy::Radial_nerve",
     "Blunt Hohmann placed laterally on the humeral shaft just above the deltoid insertion<br>"
     "Nerve directly under the retractor on the deep deltoid at the surgical neck: {{c1::anterior branch of the axillary nerve, 5 to 7 cm below the acromion}}<br>"
     "Radial nerve position at this level: {{c2::posterior, in the spiral groove at the level of the deltoid tuberosity}}<br>"
     "Retractor errors that reach the radial nerve: {{c3::tip slides distal to the tuberosity, tip levered posteriorly, tip in muscle instead of on bone}}<br>"
     "Arm position that rotates the groove toward a lateral retractor: {{c4::internal rotation}}",
     "Gerwin 1996: radial nerve contacts the posterior humerus from about 20 cm above the medial epicondyle to 14 cm above the lateral epicondyle, "
     "pierces the lateral intermuscular septum 10 cm above the lateral epicondyle. On a 30 cm humerus that is about 8 to 15 cm below the acromion. "
     "Keep the tip subperiosteal, lateral or anterolateral, proximal to the tuberosity."),
]

lines = [
    "#separator:tab",
    "#html:true",
    "#notetype:Cloze",
    f"#deck:{DECK}",
    "#tags column:3",
]
rows = []
for group, text, extra in notes:
    extra = (extra + "<br><br>" if extra else "") + "Case prep: Galatz shoulder, 10/2026"
    tags = f"CasePrep Galatz Shoulder {group}"
    for field in (text, extra):
        assert not re.search("[–—]", field), (group, "dash")
        assert not re.search(r"<(?=[\s\d=])", field), (group, "raw <")
        assert "\t" not in field and "\n" not in field
    rows.append((text, extra, tags))
    lines.append("\t".join([text, extra, tags]))

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, BASENAME + ".txt")
open(out, "w").write("\n".join(lines) + "\n")
n_cards = sum(len(set(re.findall(r"\{\{c(\d+)::", t))) for _, t, _ in notes)
print(f"{len(notes)} notes, {n_cards} cards -> {out}")

# Optional .apkg for direct import on mobile. Needs genanki (pip install genanki).
try:
    import genanki
except ImportError:
    print("genanki not installed, skipping .apkg")
    sys.exit(0)

model = genanki.Model(
    1607392319 + 7, "Cloze (Galatz case prep)",
    fields=[{"name": "Text"}, {"name": "Back Extra"}],
    templates=[{
        "name": "Cloze",
        "qfmt": "{{cloze:Text}}",
        "afmt": "{{cloze:Text}}<hr id=answer>{{Back Extra}}",
    }],
    css=".card { font-family: arial; font-size: 20px; text-align: left; color: black; background-color: white; } .cloze { font-weight: bold; color: blue; }",
    model_type=genanki.Model.CLOZE,
)
deck = genanki.Deck(2059400110 + 25, DECK)
for text, extra, tags in rows:
    deck.add_note(genanki.Note(model=model, fields=[text, extra], tags=tags.split()))
apkg = os.path.join(here, BASENAME + ".apkg")
genanki.Package(deck).write_to_file(apkg)
print(f"wrote {apkg}")
