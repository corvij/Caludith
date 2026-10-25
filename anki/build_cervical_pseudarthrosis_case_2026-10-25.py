import re

DECK = "OITE 2026::OITE 2026::2 Cases::Spine::Cervical pseudarthrosis after hybrid"
CASE = "Indications conference 10/2026: C6-7 standalone ACDF pseudarthrosis below a C5-6 arthroplasty, chronic pain host, inactive stimulators"

notes = [
    # (id, Text, Back Extra)
    ("case-01",
     "Cervical hybrid construct (arthroplasty at one level, ACDF at the next). Which level gets the fusion?<br>"
     "Fuse the level with {{c1::the worse disc collapse and facet arthrosis}}; replace {{c2::the more mobile level with healthy facets}}<br>"
     "Formal contraindications to arthroplasty at a level: {{c3::facet arthrosis, collapsed disc, instability, ossification}}",
     "In this case the arthroplasty went at C5-6 and the fusion at C6-7. A cadaver hybrid study found the arthroplasty kept near intact motion whether it sat above or below the fusion."),
    ("case-02",
     "Why is the ACDF under a cervical arthroplasty usually a standalone cage with integrated screws rather than a plate?<br>"
     "{{c1::A plate on the shared vertebral body would collide with the arthroplasty footplate}}<br>"
     "Trade-off of standalone versus plated ACDF: standalone gives {{c2::less dysphagia}} but {{c3::more subsidence and, in some series, more nonunion}}",
     "Meta-analyses: cage-only groups had less dysphagia within and beyond 3 months. Plated constructs had less subsidence and better lordosis. A 2026 two center single level cohort reported pseudarthrosis 26.7% standalone versus 3.2% plated at 12 months, not significant after adjustment."),
    ("case-03",
     "Where do most nonunions occur in a multilevel anterior cervical construct?<br>"
     "{{c1::The caudal-most level}}, involved in over {{c2::80%}} of multilevel pseudarthroses<br>"
     "Levels with intrinsically higher pseudarthrosis risk: {{c3::C5-6 and C6-7}}",
     "In a four level ACDF series without posterior fixation, C6-7 was the nonunion site in 46.8%. In this case the weakest construct, a standalone cage, sat at C6-7, the caudal level."),
    ("case-04",
     "CT signs of pseudarthrosis around an interbody cage<br>"
     "{{c1::No trabecular bone crossing the disc space through or around the cage}}<br>"
     "{{c2::Lucent halos around the screws}}<br>"
     "{{c3::A gap or cleft between the cage and the endplate or posterior annulus}}<br>"
     "Why a fibrous nonunion with integrated screws can read as no excessive motion on flexion and extension: {{c4::the screws hold it}}",
     "Thin cut axials and a coronal reformat through the cage are the formal confirmation. The CT report in this case never addressed bridging bone; it read the hardware as intact and stopped."),
    ("case-05",
     "Flexion and extension radiographs for cervical pseudarthrosis<br>"
     "Measurement: {{c1::interspinous distance change between flexion and extension}}<br>"
     "Threshold: {{c2::more than 1 mm}}<br>"
     "Which study cannot diagnose a nonunion: {{c3::MRI}}",
     "A radiology read of no excessive motion is not a measurement. Films must be at matched magnification. In this case the MRI report never used the word nonunion; the clinic note attributed it to the MRI."),
    ("case-06",
     "Natural history of ACDF pseudarthrosis, Phillips et al, Spine 1997<br>"
     "Symptomatic at mean 5 years: {{c1::67%}}<br>"
     "Asymptomatic: {{c2::33%}}<br>"
     "Predictor of becoming symptomatic: {{c3::younger age}}",
     "48 patients. Longer follow-up data summarized in 2020: about 80% of radiographic nonunions at 24 months had no index level reoperation over 8 years. Hecht's counseling pearl: most nonunions are asymptomatic."),
    ("case-07",
     "Revision of anterior cervical pseudarthrosis, posterior versus anterior<br>"
     "Brodsky 1992: posterior fused {{c1::94%}}, anterior {{c2::76%}}<br>"
     "Carreon 2006: re-revision for persistent nonunion {{c3::12 of 27 anterior}} versus {{c4::2 of 93 posterior}}<br>"
     "Cost of posterior: {{c5::more blood loss, longer stay, 8% versus 4% complications}}",
     "Elder 2016: 22 posterior revisions, all fused, median 10 months. McAnany 2015: posterior fused more often but clinical improvement did not differ, attributed to residual anterior root compression."),
    ("case-08",
     "What a posterior cervical fusion does not do for an anterior pseudarthrosis<br>"
     "{{c1::It does not remove a disc fragment or osteophyte complex behind the cage}}<br>"
     "When that matters: {{c2::when the anterior lesion is producing a radiculopathy or myelopathy}}<br>"
     "When it does not: {{c3::axial pain from the nonunion with no critical stenosis, intact exam, and electrically normal roots at that level}}",
     "In this case the C6-7 osteophyte complex caused subtle sac effacement, the exam was intact, and triceps and pronator teres were electrically normal. The pain at that level is axial."),
    ("case-09",
     "Anterior cervical revision through a prior approach<br>"
     "Before choosing the side: {{c1::ENT laryngoscopy to check the vocal cords}}<br>"
     "Prior left approach, left cord intact: {{c2::go right}}<br>"
     "Prior left approach, left cord paralyzed: {{c3::go back left}}<br>"
     "Occult infection rate in one anterior revision series: {{c4::about 40%}}",
     "A paralyzed cord on the prior side means the contralateral recurrent laryngeal nerve is the only working one; injuring it is bilateral palsy. Send ESR, CRP, and intraoperative cultures. In this case the clips on CT sat left of midline at C6-7."),
    ("case-10",
     "Cervical arthroplasty failure, what to look for on films<br>"
     "{{c1::Heterotopic ossification}}, reported in roughly {{c2::7 of 10}} devices over time<br>"
     "At 10 years in blinded European trials, {{c3::over half}} of replacements had spontaneously fused<br>"
     "A working arthroplasty on flexion and extension shows {{c4::the core space changing shape between positions}}",
     "Hecht's argument: any single subaxial level is 7 to 8% of cervical motion, the unconflicted studies show no adjacent segment benefit, and no device lasts 40 years. If an arthroplasty has ossified, fusing across it costs nothing."),
    ("case-11",
     "Hecht's anti-arthroplasty argument, the six layers<br>"
     "1. Motion accounting: {{c1::half of cervical motion is occiput to C2; one subaxial level is 7 to 8%}}<br>"
     "2. {{c2::Conflict of interest stratification: unconflicted studies show no ASD difference}}<br>"
     "3. {{c3::Blinded allocation European trials: no degeneration difference at 5 years}}<br>"
     "4. {{c4::Heterotopic ossification about 7 in 10}}<br>"
     "5. {{c5::Device longevity versus a 40 year horizon}}<br>"
     "6. {{c6::Postoperative motion improves in both groups and neither reaches normal}}",
     "Counter position, from the same institution: motion preservation is exactly the tool for the adjacent segment problem, and several meta-analyses report lower CDA reoperation at some follow-ups. The deck answer argues both sides."),
    ("case-12",
     "A symptom is not a diagnosis. Localize before you attribute. Applied to a neck patient with hand tingling<br>"
     "Conduction findings that are peripheral, not cervical: {{c1::prolonged median sensory distal latency at the wrist (carpal tunnel)}} and {{c2::ulnar slowing across the elbow}}<br>"
     "What a cervical fusion does for those: {{c3::nothing}}",
     "Two conduction studies in this case showed bilateral carpal tunnel and ulnar sensory slowing. Part of his arm numbness is peripheral. That belongs in the counseling, not in the fusion plan."),
    ("case-13",
     "Needle EMG with fibrillations in deltoid bilaterally and biceps, triceps and brachioradialis spared, normal recruitment and motor unit morphology<br>"
     "Root: {{c1::C5, possibly C6}}<br>"
     "Stage: {{c2::active denervation without chronic reinnervation}}<br>"
     "Foramen the C5 root exits: {{c3::C4-5}}<br>"
     "Rule for cervical root exit: {{c4::C1 to C7 exit above the same numbered pedicle; C8 exits below C7}}",
     "Deltoid and biceps both carry C5 and C6, so the C6 root at a C5-6 arthroplasty level, unreadable on MRI through artifact, is the other candidate. Paraspinals were not sampled. The finding was subclinical with 5/5 strength and normal reflexes, and was flagged as needing corroboration."),
    ("case-14",
     "Posterior cervical foraminotomy, when it works and why the lumbar analogy fails<br>"
     "Indication: {{c1::a foraminal or far lateral lesion}}<br>"
     "Why it fails for central or paracentral compression: {{c2::the cord cannot be retracted}}<br>"
     "Where it fits in this case: {{c3::bilateral C4-5 foraminotomies for electrically confirmed C5 radiculopathy, without fusing C4-5}}",
     "Hecht's framing: in the lumbar spine you are below the conus and can retract the sac; above it you cannot. Posterior foraminotomy carries a higher reoperation rate than ACDF but preserves the segment."),
    ("case-15",
     "Radiographic adjacent segment degeneration versus symptomatic adjacent segment disease after cervical fusion<br>"
     "Most radiographic adjacent change {{c1::stays asymptomatic}}<br>"
     "Adjacent level reoperation after cervical fusion in long term cohorts: roughly {{c2::6% at 14 years}}<br>"
     "Evidence for fusing a mild, stable adjacent level prophylactically: {{c3::none}}",
     "The adjacent discs are already overloaded before surgery because the diseased segment is stiff. In this case C4-5 was a mild right foraminal finding, stable since 2024, and C3-4 looked the same bilaterally."),
    ("case-16",
     "Spinal cord stimulator and MRI<br>"
     "What decides whether a patient can be scanned: {{c1::the specific generator and lead models and the manufacturer's labeled conditions}}<br>"
     "Listed exclusions for at least one current system: {{c2::more than one generator}} and {{c3::any abandoned lead, extension, or adapter}}<br>"
     "A patient already scanned with the system in place: {{c4::record those conditions and change nothing in the system before the repeat}}",
     "Some systems are labeled head or extremity only. This patient had a cervical MRI at 1.5 T with two generators and three arrays in place in March 2026."),
    ("case-17",
     "Stimulator lead in the posterior epidural canal across the levels of a planned posterior cervical fusion<br>"
     "Options: {{c1::explant before surgery, explant and replace after fusion, or protect it in the field}}<br>"
     "When explant in the same sitting is the clean answer: {{c2::the system is inactive and causes pocket pain}}<br>"
     "Who should be in the decision: {{c3::the implanting pain physician}}",
     "Send pocket cultures at explant. An implanted lead and generators raise the stakes of a posterior wound infection; deep stimulator infections usually end in explant."),
    ("case-18",
     "Host factors that predict worse outcomes after cervical fusion<br>"
     "{{c1::Chronic preoperative opioid therapy}}: prolonged postoperative opioid use and worse outcomes at 1 and 2 years<br>"
     "{{c2::Longer preoperative opioid duration}}: lower return to work after single level fusion<br>"
     "{{c3::Preoperative antidepressant use}}: more opioid use, complications, and reoperation in a propensity matched national cohort",
     "None of these say do not operate. They say the expected gain is smaller, the goal should be written down before surgery, and an opioid plan and psychological evaluation belong in the work-up regardless of the operation."),
    ("case-19",
     "Opportunistic CT Hounsfield units before spinal instrumentation<br>"
     "Most replicated threshold for mechanical and junctional complications: about {{c1::118 HU}}<br>"
     "Risk below it: roughly {{c2::2.8 fold}}<br>"
     "Where to measure in a cervical case with hardware at C5 to C7: {{c3::C3 and C4 bodies, away from the implants}}",
     "A chronic T12 wedge deformity at 52 is a reason to get the number. Cage subsidence cutoffs run higher, around 135 to 200 HU in different series."),
    ("case-20",
     "Ending a posterior cervical construct at C7 versus crossing to T1<br>"
     "Reasons to cross: {{c1::thin C7 lateral masses, degenerate C7-T1, long construct, poor bone}}<br>"
     "What to check on the CT: {{c2::C7 lateral mass dimensions and the C7-T1 facets}}<br>"
     "Junctional principle: {{c3::a rigid construct offloads stress onto the mobile segment next to it}}",
     "Same physics as proximal junctional kyphosis and adjacent segment disease. In this case C7-T1 had bilateral facet arthrosis on CT and a disc osteophyte on MRI."),
    ("case-21",
     "Hecht's restraint principle<br>"
     "{{c1::Treat the symptomatic driver; fuse only the unstable segment; extend a construct only as far as the failed or at risk bone requires}}<br>"
     "Master discriminator for fuse versus decompress: {{c2::what is unstable? Instability or nonunion, fuse. Compression in a stable spine, decompress}}",
     "Applied here: the nonunion at C6-7 gets fused. The arthroplasty level is included only if it has ossified or fixation demands it. C4-5 is fused only if the C5 radiculopathy is corroborated and a foraminotomy will not do."),
    ("case-22",
     "Hybrid cervical surgery versus two level ACDF, 2025 meta-analysis of 11 studies<br>"
     "Hybrid showed {{c1::better motion preservation and less adjacent segment motion}}, with {{c2::similar clinical scores and complication rates}}<br>"
     "Failure pattern in a 115 hybrid series at 6.5 years: {{c3::5 reoperations for adjacent segment disease, 1 for pseudarthrosis at the fused level}}",
     "Hybrids carry more heterotopic ossification than fusion alone and long term survivorship data are thin. This case shows the fused level failing, the arthroplasty ossifying, and the adjacent level being blamed, all at once."),
    ("case-23",
     "Neuromonitoring and setup for a posterior cervical fusion with stimulator removal, as booked<br>"
     "Modalities: {{c1::SSEP, EMG, and MEP}}<br>"
     "Table: {{c2::Jackson}}<br>"
     "Why baselines before and after positioning matter in a degenerate neck: {{c3::prone positioning and neck flexion can change signals before the incision}}",
     "Navigation and Cell Saver were on the booking. Planned time 3 hours 30 minutes, two day stay."),
    ("case-24",
     "The case in one card. 52 year old man, hybrid C5-6 arthroplasty with standalone C6-7 ACDF 11 years ago, told it never healed<br>"
     "Secure diagnosis: {{c1::C6-7 fibrous nonunion on CT with an osteophyte complex behind the cage}}<br>"
     "Electrical finding: {{c2::subclinical bilateral C5 denervation, uncorroborated, plus bilateral carpal tunnel}}<br>"
     "Booked operation: {{c3::posterior fusion C4 to C7 with removal of the cervical stimulator}}<br>"
     "Level to argue: {{c4::C4, resting on one EMG and a mild stable foraminal finding}}<br>"
     "Host: {{c5::chronic opioids, disability, two inactive stimulators, three lumbar operations}}",
     "Alternative construct: posterior fusion of the failed levels, C5 to C7 if the arthroplasty has ossified, bilateral C4-5 foraminotomies if the C5 radiculopathy is confirmed, cervical stimulator out. Anterior revision only if the osteophyte complex is proven to be the pain generator."),
]

lines = [
    "#separator:tab",
    "#html:true",
    "#notetype:Cloze",
    f"#deck:{DECK}",
    "#tags column:3",
]
for cid, text, extra in notes:
    extra = f"{extra}<br><br>Source: {CASE}"
    tags = f"Spine Cervical Case Pseudarthrosis Hybrid Case::{cid}"
    for field in (text, extra):
        assert not re.search("[–—]", field), (cid, "dash")
        assert not re.search(r"<(?=[\s\d=])", field), (cid, "raw <")
        assert "\t" not in field and "\n" not in field
    lines.append("\t".join([text, extra, tags]))

out = "cervical_pseudarthrosis_case_2026-10-25.txt"
open(out, "w").write("\n".join(lines) + "\n")
n_cards = sum(len(set(re.findall(r"\{\{c(\d+)::", t))) for _, t, _ in notes)
print(f"{len(notes)} notes, {n_cards} cards -> {out}")
