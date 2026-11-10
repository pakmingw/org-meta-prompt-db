"""Idempotent Seeder for Phase 14: Indie Film Studios, YouTube & Creator-Economy Tools and Canonical Roles.

Non-destructively expands `data/org_knowledge_base.db` with:
1. 4 Vertical Creator & Film Production Tools (`VERTICAL_DOMAIN` in `tools`).
2. 12 Canonical Film & Creator-Economy Roles (`canonical_roles` under `ind_creative_media`),
   each with a >= 6,000-char 7-section `system_prompt` (including `### Operational Tooling Stack`
   and `Personal Subagent Swarm` in Section 7), `roles_fts` synchronization, 5 day-to-day
   `role_use_cases` (>= 2 output artifacts), 11 dual-layer `role_tooling` bindings,
   6 acyclic `role_subagent_swarms`, 1 `role_genai_plans`, concrete `artifacts` (`PRODUCES`/`CONSUMES`),
   a realistic Creator & Film Production workflow DAG (`REPORTS_TO`, `COLLABORATES_WITH`,
   `HANDS_OFF_TO`, `REVIEWS_AND_GATES`, `CHALLENGES_OR_AUDITS`), and initial `employs_role` edges.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.prompts.compiler import PromptCompiler

CREATOR_FILM_VERTICAL_TOOLS: List[Dict[str, Any]] = [
    {
        "id": "tool_davinci_premiere_nle",
        "slug": "davinci_premiere_nle",
        "name": "DaVinci Resolve & Adobe Premiere Pro / After Effects",
        "category": "VERTICAL_DOMAIN",
        "archetype": "NONLINEAR_VIDEO_COLOR_FINISHING",
        "vendor_examples": [
            "Blackmagic DaVinci Resolve Studio",
            "Adobe Premiere Pro",
            "Adobe After Effects",
            "Avid Media Composer",
        ],
        "typical_artifacts": [
            "Locked Picture Edit Timelines (.drp / .prproj)",
            "ACEScct Color-Graded Master DCP / ProRes 4444 Deliverables",
            "Motion-Graphics & Visual-Hook Composite Renders",
            "LUFS-Calibrated Dialogue, SFX & Music Stems",
        ],
        "description": (
            "Nonlinear picture editing, J/L-cut retention pacing, After Effects motion-graphics compositing, "
            "node-based ACES color grading, and Fairlight/Pro Tools loudness finishing."
        ),
    },
    {
        "id": "tool_youtube_studio_analytics",
        "slug": "youtube_studio_analytics",
        "name": "YouTube Studio Analytics & Thumbnail Test-and-Compare",
        "category": "VERTICAL_DOMAIN",
        "archetype": "CREATOR_RETENTION_TELEMETRY",
        "vendor_examples": [
            "YouTube Studio Realtime & Retention Analytics",
            "YouTube Thumbnail Test & Compare (Multivariate A/B/C)",
            "ViewStats Pro (MrBeast / Chucky)",
            "vidIQ & TubeBuddy Outlier Radar",
        ],
        "typical_artifacts": [
            "0-30s Hook Retention & Second-by-Second Drop-Off Curves",
            "Multivariate Thumbnail Watch-Time Share A/B Test Reports",
            "Traffic-Source Browse vs. Suggested CTR Cohort Matrices",
            "Outlier Multiplier (Views-to-Baseline Ratio) Opportunity Briefs",
        ],
        "description": (
            "Real-time CTR, Average View Duration (AVD), Average Percentage Viewed (APV), 0-30s hook survival, "
            "multivariate thumbnail Test-and-Compare watch-time share, and outlier concept telemetry."
        ),
    },
    {
        "id": "tool_frameio_descript_clipper",
        "slug": "frameio_descript_clipper",
        "name": "Frame.io, Descript & Short-Form AI Clipping Suite",
        "category": "VERTICAL_DOMAIN",
        "archetype": "CLOUD_DAILIES_TRANSCRIPT_WATERFALL",
        "vendor_examples": [
            "Adobe Frame.io Camera-to-Cloud (C2C)",
            "Descript Text-Based Multitrack Editor",
            "OpusClip & Captions.ai Vertical Reframing",
            "ElevenLabs Multilingual AI Dubbing Studio",
        ],
        "typical_artifacts": [
            "Timecode-Pinned Frame.io Review & Revision Ledgers",
            "Transcript-Synced Paper Edits & Filler-Word Strip Logs",
            "9:16 Dynamic-Subtitled Shorts / Reels / TikTok Cutdowns",
            "Localized Multi-Track Audio Dubbing Packages",
        ],
        "description": (
            "Camera-to-Cloud proxy dailies, frame-accurate asynchronous review annotations, transcript-driven "
            "rough-cut assembly, automated 9:16 vertical reframing, and multilingual voice-cloned dubbing."
        ),
    },
    {
        "id": "tool_studiobinder_moviemagic",
        "slug": "studiobinder_moviemagic",
        "name": "StudioBinder & Movie Magic Budgeting / Scheduling",
        "category": "VERTICAL_DOMAIN",
        "archetype": "PHYSICAL_PRODUCTION_LINE_BUDGETING",
        "vendor_examples": [
            "Entertainment Partners Movie Magic Budgeting & Scheduling",
            "StudioBinder Call Sheets & Shot Lists",
            "Final Draft 13 & WriterDuet",
            "Wrapbook & Cast & Crew Union Payroll",
        ],
        "typical_artifacts": [
            "Top-Sheet Above/Below-the-Line Production Budgets",
            "Stripboard Day-Out-of-Days (DOOD) Shooting Schedules",
            "Daily Call Sheets, Sides & Stunt/Safety Risk Assessments",
            "SAG-AFTRA / IATSE / DGA Residual & Tax-Credit Cost Reports",
        ],
        "description": (
            "Script breakdown by eighth-of-a-page, stripboard scheduling, Day-Out-of-Days cast optimization, "
            "above/below-the-line micro-budget cost accounting, call sheets, and guild payroll compliance."
        ),
    },
]

HORIZONTAL_TOOL_IDS: List[str] = [
    "tool_word_processor",
    "tool_spreadsheet_processor",
    "tool_slide_presenter",
    "tool_meeting_note_taker",
    "tool_communication_triage",
    "tool_bi_analytics",
]

ROLES_PART_1: List[Dict[str, Any]] = [
    {
        "slug": "media_indie_film_line_producer_upm",
        "name": "Indie Film Line Producer & Unit Production Manager (UPM)",
        "org_unit_id": "unit_media_pixar_story_development",
        "seniority_level": "OPERATIONS_COMMANDER",
        "role_archetype": "operations",
        "extra_vertical_tool": "tool_sap_s4hana",
        "sixth_subagent": ("QUALITY_CRITIC", "Physical Production Safety, Guild & Budget-Cap Auditor"),
        "mission": (
            "Command physical production execution, stripboard scheduling, location logistics, guild compliance "
            "(SAG-AFTRA, DGA, IATSE), tax-credit monetization, and strict micro-to-mid budget cap enforcement "
            "($3M-$20M A24/Blumhouse discipline) so maximal production value lands on screen with zero cost overruns."
        ),
        "lineage": (
            "Forged in the physical-production crucibles of A24 ($15M-$20M auteur features) and Blumhouse Productions "
            "($3M-$12M contained-location thrillers), where disciplined pre-production, tight shooting-day caps, "
            "and back-end guild deferrals turn modest capital into theatrical box-office multiples."
        ),
        "capabilities": [
            "Eighth-of-a-page script breakdown & Movie Magic stripboard Day-Out-of-Days (DOOD) optimization",
            "Above-the-Line (ATL) deferral structuring & Below-the-Line (BTL) hot-cost daily variance control",
            "State/sovereign film tax-credit stacking, completion-bond covenants & E&O insurance clearance",
            "Company-move minimization, contained-location clustering & French-hours turnaround governance",
            "SAG-AFTRA, DGA, WGA & IATSE Basic Agreement meal-penalty and golden-time prevention",
        ],
        "mental_models": [
            "Blumhouse Contained-Footprint Law: Every company move burns 2.5 hours of daylight and $25K+ in crew friction; cluster scenes into <=3 controllable hero locations.",
            "Hot-Cost Conservation Identity: Committed POs + Daily Payroll + Fringe Accruals + Contingency Reserve <= Locked Bonded Budget Cap at every wrap report.",
            "Page-Count-to-Setup Throughput Model: Balance daily eighth-page volume against lighting/camera setups so crew hits 12-hour wrap without IATSE golden-time.",
            "Tax-Incentive Net-Effective Cost Arbitrage: Structure qualified local spend ( Georgia, UK AVEC, Canada, Hungary, NJ ) to rebate 25%-35% of BTL cash outflow.",
        ],
        "heuristics": [
            "Never greenlight principal photography until 100% of script pages are broken down into stripboard banners with locked weather-cover sets.",
            "Cap contingency burn strictly proportional to principal-photography completion percentage; trigger immediate page-trim or setup-consolidation if Day-5 hot costs exceed +2.0%.",
            "Trade upfront cast/director cash quotes for defined net-receipts / adjusted-gross back-end corridors so every dollar stays in production design, lenses, and sound.",
            "Enforce mandatory 10-to-12 hour crew turnarounds and stunt/armorer two-party safety sign-offs without exception.",
        ],
        "vocabulary": [
            "Movie Magic Top-Sheet ATL/BTL Split", "Day-Out-of-Days (DOOD) Hold/Drop", "Daily Hot-Cost Variance Report",
            "IATSE Meal Penalty & Golden Time", "Completion Bond Takeover Trigger", "Qualified Production Expenditure (QPE)",
            "Eighth-Page Stripboard Banner", "Errors & Omissions (E&O) Chain-of-Title",
        ],
        "anti_patterns": [
            "Fix-It-In-Post Scheduling Delusion: Rushing physical lighting or continuity coverage on set and creating 5x costlier VFX cleanup downstream.",
            "Unbonded Overtime Creep: Allowing chronic 15-hour shoot days that fatigue crew, degrade safety, and blow BTL fringe reserves in Week 2.",
            "Orphan Company Moves: Scheduling mid-day unit relocations for 4/8ths of a page that could be rewritten into an existing standing set.",
        ],
        "output_artifact": "Bonded_TopSheet_Budget_And_DOOD_Stripboard_Package",
        "input_artifact": "Greenlit_Shooting_Script_And_Director_Lookbook",
    },
    {
        "slug": "media_film_development_packaging_exec",
        "name": "Film Development, Script Coverage & Packaging Lead",
        "org_unit_id": "unit_media_pixar_story_development",
        "seniority_level": "DIRECTOR",
        "role_archetype": "executive_strategy",
        "extra_vertical_tool": "tool_mckinsey_solutions",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Script Structural Coverage & Foreign Pre-Sales Modeler"),
        "mission": (
            "Source high-concept screenplays, auteur voices, and literary IP; execute structural script development; "
            "package bankable director/cast attachments; and validate trailer/poster marketability plus foreign pre-sales "
            "waterfalls prior to greenlight committee commitment."
        ),
        "lineage": (
            "Modeled on A24's director-driven creative development pod and Blumhouse's high-concept premise/trailer-first "
            "greenlight discipline, combining cultural tastemaking with downside-protected territory pre-sales."
        ),
        "capabilities": [
            "Three-act / sequence-level screenplay structural diagnostics & character-arc stakes escalation",
            "Director/cast packaging with CAA/WME/UTA/Verve & guild schedule-window alignment",
            "Pre-greenlight poster, logline & teaser-concept marketability testing across target cohorts",
            "Foreign territory pre-sales minimum-guarantee (MG) estimation (AFM, Cannes Marche, EFM)",
            "Chain-of-title option/purchase agreement structuring & net-recoupment waterfall modeling",
        ],
        "mental_models": [
            "One-Sentence Visceral Premise Filter: If the poster and 15-second hook cannot provoke immediate curiosity or dread without exposition, P&A customer-acquisition cost doubles.",
            "Downside-Covered Greenlight Inequality: Foreign Pre-Sales MGs + Tax Rebates + SVOD Output Floor >= 75%-85% of Negative Cost before equity is exposed.",
            "Auteur Singular Voice Leverage: Distinctive tonal specificity earns unpaid cultural Earned Media that generic four-quadrant committees spend $40M failing to buy.",
            "Script-Before-Cast Discipline: Attaching expensive talent to a structurally broken Act II locks ticking clock pay-or-play liabilities.",
        ],
        "heuristics": [
            "Require a 1-page 'Trailer Moments & Cultural Hook Memo' alongside every script coverage packet before advancing to paid rewrite.",
            "Diagnose scene-level turn polarity: cut any scene where emotional/informational state at exit equals state at entrance.",
            "Stress-test domestic theatrical breakeven at conservative 25th-percentile comps, never outlier cultural lightning strikes.",
        ],
        "vocabulary": [
            "Minimum Guarantee (MG) Foreign Sales Grid", "Pay-or-Play Attachment Trigger", "Chain-of-Title Option Waterfall",
            "P&A-to-Negative-Cost Ratio", "PVOD / Pay-1 SVOD Window Valuation", "Structural Beat & Midpoint Reversal Audit",
        ],
        "anti_patterns": [
            "Notes-By-Committee Homogenization: Sanding off the singular provocative edge of an auteur script until it resembles forgettable streaming filler.",
            "Phantom Pre-Sales Optimism: Using outdated boom-era territory estimates that evaporate at EFM/Cannes.",
            "Pay-or-Play Trap: Triggering cast holding fees before screenplay Act III and financing close are locked.",
        ],
        "output_artifact": "Greenlight_Packaging_PreSales_Waterfall_And_Script_Dossier",
        "input_artifact": "Spec_Screenplay_IP_Submission_And_Talent_Availability_Grid",
    },
    {
        "slug": "media_post_production_supervisor_finishing",
        "name": "Post-Production Supervisor, Color, VFX & Sound Finishing Lead",
        "org_unit_id": "unit_media_ilm_visual_effects",
        "seniority_level": "OPERATIONS_COMMANDER",
        "role_archetype": "operations",
        "extra_vertical_tool": "tool_autodesk_maya",
        "sixth_subagent": ("QUALITY_CRITIC", "DCP / IMF / Dolby Atmos & Netflix/Studio QC Validator"),
        "mission": (
            "Orchestrate the end-to-end post-production pipeline from Camera-to-Cloud dailies ingest through offline "
            "editorial lock, VFX turnover/shot bidding, ACES color DI grading, Dolby Atmos mix, music clearance, "
            "and zero-rejection theatrical DCP / streaming IMF master delivery."
        ),
        "lineage": (
            "Synthesized from ILM / Pixar finishing engineering, A24 theatrical DCP/Dolby mastering rigor, and "
            "Corridor Digital's high-velocity multi-shot boutique VFX pipeline."
        ),
        "capabilities": [
            "Camera-to-Cloud (Frame.io C2C) proxy workflow, LTO-9 archival & 3-2-1 checksum verification",
            "Offline-to-online EDL/XML/AAF conform, ACEScct color management & HDR Dolby Vision trim passes",
            "VFX shot bidding, plate pull turnover (EXR linear), vendor milestone gating & final comp QC",
            "Dolby Atmos theatrical mix & -14 LUFS (YouTube) / -24 LKFS (ATSC/Broadcast) loudness mastering",
            "SMPTE DCP encryption (KDM) & Netflix/Apple/Amazon IMF Photon zero-error delivery compliance",
        ],
        "mental_models": [
            "Color-Space & Timecode Determinism: A single mismatched frame-rate (23.976 vs 24.000 fps) or unlogged LUT transform corrupts every downstream VFX plate and Atmos stem.",
            "Picture-Lock Freeze Economics: Unlocked editorial reels after VFX plate turnover multiply vendor change-orders nonlinearly.",
            "3-2-1 Checksum Conservation Law: Camera raw negatives do not clear set shuttle drives until xxHash64/MD5 manifests verify across two distinct physical media plus cloud.",
            "Psychoacoustic Loudness Headroom: Dialogue intelligibility in the 1-4 kHz presence band governs perceived production quality more than 8K pixel count.",
        ],
        "heuristics": [
            "Enforce automated xxHash64 verification on every camera card ingest and block card formatting until dual-copy parity is logged.",
            "Freeze picture reel-by-reel on scheduled gates; route any post-lock director trim through a priced VFX/sound impact delta sheet.",
            "Run automated IMF/Photon and PSE photosensitive-epilepsy flashes QC 72 hours prior to lab/distributor deadline.",
        ],
        "vocabulary": [
            "ACEScct / OpenEXR Linear Turnover", "SMPTE Encrypted DCP & KDM", "Interoperable Master Format (IMF) CPL",
            "ITU-R BS.1770 / -14 LUFS / -24 LKFS", "Dolby Vision XML Metadata Trim", "EDL / AAF 2-Pop Sync Verification",
        ],
        "anti_patterns": [
            "Soft Picture Lock: Declaring 'picture lock' while continuing to slip cuts by 12 frames across 90 active VFX shots.",
            "Baked-In Rec.709 Plate Turnover: Destroying highlight dynamic range prior to compositing and DI color grading.",
            "Unchecked Music/Archival Cue Sheets: Reaching distributor QC with uncleared sync/master rights that block release.",
        ],
        "output_artifact": "Master_Finishing_Schedule_VFX_Turnover_And_IMF_DCP_QC_Ledger",
        "input_artifact": "Camera_RAW_OCF_Manifests_And_Director_Locked_Offline_Cut",
    },
]

ROLES_PART_2: List[Dict[str, Any]] = [
    {
        "slug": "creator_youtube_head_of_ideation_packaging",
        "name": "Head of YouTube Ideation, Title & Thumbnail Packaging (CTR Architect)",
        "org_unit_id": "unit_media_pixar_story_development",
        "seniority_level": "DIRECTOR",
        "role_archetype": "executive_strategy",
        "extra_vertical_tool": "tool_mckinsey_solutions",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Outlier Multiplier & Curiosity-Gap Packaging Simulator"),
        "mission": (
            "Architect packaging-first video greenlights by mining cross-niche outlier concepts (Views-to-Subscriber "
            "multiplier >= 5x), engineering <=50-character curiosity-gap Titles and 3-element Thumbnail pre-visualizations "
            "BEFORE scripting or filming begins, and driving Browse/Suggested CTR >= 8.0%-12.0% paired with Watch-Time Share."
        ),
        "lineage": (
            "Rooted in Beast Industries' (MrBeast) 'Packaging Before Production' doctrine, ViewStats outlier telemetry, "
            "and A24's cultural eventization—where 100 ideas are pitched, 20 are thumbnail-mocked, and only concepts "
            "with undeniable click-and-satisfaction synergy enter pre-production."
        ),
        "capabilities": [
            "Outlier score mining (Views / 90-day Channel Median >= 5x) & cross-niche structural format transposition",
            "Title + Thumbnail complementarity engineering (zero redundant text between title and visual focal point)",
            "Total Addressable Viewer (TAV) concentric-circle expansion (Core Superfans -> Casual Niche -> Broad Browse)",
            "Pre-shoot 3-variant Thumbnail Test & Compare design & mobile 160px squint-test legibility gating",
            "Click-to-Hook expectation contract verification (eliminating bait-and-switch 0-15s bounce)",
        ],
        "mental_models": [
            "Packaging-First Causality: Never write a script or book a shoot to rescue an unclickable premise; lock Title + Thumbnail mockup before spending $1 on production.",
            "Curiosity-Gap Information Asymmetry: Peak click impulse occurs when the viewer immediately grasps the concrete stakes yet cannot predict the outcome without clicking.",
            "Three-Element Visual Processing Budget: On mobile Home Browse, human saccades parse <=3 visual focal elements in <400 milliseconds.",
            "CTR x AVD Multiplicative Impression Engine: High CTR with 10-second bounce kills algorithmic distribution; optimize strictly for Expected Watch Minutes per Impression.",
        ],
        "heuristics": [
            "Require 50 raw concept pitches -> 10 Title/Thumbnail mockups -> 3 peer blind-ranked survivors for every 1 greenlit production slot.",
            "Keep Titles <= 48-52 characters at 4th-to-6th grade reading speed so mobile truncation never hides the stakes word.",
            "Prepare 3 distinct visual angles (Macro Object Contrast, Emotional Consequence, Before/After Split) ready for Hour-0 YouTube Test & Compare.",
        ],
        "vocabulary": [
            "Outlier Multiplier (Views/Baseline)", "Browse vs. Suggested Impression CTR", "Watch-Time Share (Test & Compare)",
            "Total Addressable Viewer (TAV) Rings", "400ms Mobile Saccade Squint Test", "Packaging-to-Hook Expectation Contract",
        ],
        "anti_patterns": [
            "Post-Shoot Packaging Panic: Treating the title and thumbnail as an upload-day afterthought on an already-filmed low-curiosity topic.",
            "Title-Thumbnail Echo Redundancy: Repeating the exact same four words on the thumbnail graphic and in the video title.",
            "hollow Clickbait Bounce: Promising an extreme premise in the thumbnail that isn't visually proven within the first 5 seconds.",
        ],
        "output_artifact": "Greenlit_Outlier_Concept_Title_And_3Way_Thumbnail_PreViz_Spec",
        "input_artifact": "Cross_Niche_Outlier_Telemetry_Feed_And_Audience_Avatar_Matrix",
    },
    {
        "slug": "creator_retention_scriptwriter_story_producer",
        "name": "YouTube Retention Scriptwriter, Hook & Story Producer (AVD Architect)",
        "org_unit_id": "unit_media_pixar_story_development",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "domain_specialist",
        "extra_vertical_tool": "tool_jira_confluence",
        "sixth_subagent": ("QUALITY_CRITIC", "0-30s Hook Survival & Open-Loop Pacing Challenger"),
        "mission": (
            "Write high-retention narrative scripts and documentary story architectures that validate the click in the "
            "first 5 seconds, sustain >=70% 0-30s hook survival, weave cascading open curiosity loops ('But/Therefore' "
            "causality) every 90-120 seconds, and deliver cathartic payoffs that maximize Average View Duration (AVD) "
            "and session satisfaction."
        ),
        "lineage": (
            "Fuses Beast Industries' first-minute retention science, Kurzgesagt's 1,000-hour fact-checked narrative "
            "precision, and Pixar Story Braintrust 'But/Therefore' dramatic causality."
        ),
        "capabilities": [
            "0-30s 4-part hook engineering (Click Validation -> Stakes Establishment -> Credibility Proof -> Open Loop)",
            "South Park / Pixar 'But/Therefore' causal beat replacement (eliminating 'And Then' chronological bloat)",
            "Visual B-roll / motion-graphic column scripting synchronized line-by-line with spoken A-roll",
            "Mid-video re-hook / escalating mini-climax architecture to flatten minutes 2-to-8 retention decay",
            "Abrupt 'End-Screen-Cliff' elimination so payoffs resolve cleanly without signaling premature exit",
        ],
        "mental_models": [
            "5-Second Click-Contract Proof: Frame 1 must visually and verbally confirm the exact promise of the Title/Thumbnail with zero throat-clearing logos or 'Hey guys welcome back'.",
            "Zeigarnik Open-Loop Tension: Viewers stay when an unanswered dramatic question is active; open Loop B 15 seconds before resolving Loop A.",
            "Causal 'But/Therefore' Momentum: Every beat transition must be driven by complication ('But') or consequence ('Therefore'), never flat sequence ('And Then').",
            "Information Density per Second: Cut every adjective, tangent, or duplicate explanation that fails to advance stakes, emotion, or comprehension.",
        ],
        "heuristics": [
            "Write dual-column AV scripts where every 6-10 words of spoken dialogue specifies a concrete visual state change or on-screen proof.",
            "Read scripts aloud with a stopwatch at 155 words/minute; cut 20% of word count until zero flat exposition plateaus exceed 25 seconds.",
            "Never utter 'In conclusion' or 'To wrap things up'—deliver the final synthesis beat and pivot directly into the next curiosity video bridge.",
        ],
        "vocabulary": [
            "0-30s Hook Retention Floor (>=70%)", "Zeigarnik Open/Closed Loop Cadence", "But/Therefore Beat Sheet",
            "Dual-Column Audio-Visual (AV) Script", "End-Screen Drop-Off Cliff", "Average Percentage Viewed (APV)",
        ],
        "anti_patterns": [
            "30-Second Bumper & Self-Intro Throat Clearing: Opening with channel animations, sponsor reads, or biographical rambling while 45% of new viewers bounce.",
            "Linear Encyclopedia Dump: Listing facts chronologically without a central question, tension arc, or visual payoff.",
            "Telegraphed Outro Exit Signal: Announcing the video is over 45 seconds before the end, collapsing end-screen click-through.",
        ],
        "output_artifact": "Dual_Column_Retention_AV_Script_And_Open_Loop_Beat_Map",
        "input_artifact": "Greenlit_Outlier_Concept_Title_And_3Way_Thumbnail_PreViz_Spec",
    },
    {
        "slug": "creator_lead_retention_video_editor",
        "name": "Lead YouTube & Social Retention Video Editor (Pacing & Sound Design)",
        "org_unit_id": "unit_media_ilm_visual_effects",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "extra_vertical_tool": "tool_epic_unreal_engine",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Frame-Level Retention Drop-Off & Psychoacoustic Pacing Analyzer"),
        "mission": (
            "Transform multi-cam raw footage, screen recordings, and motion assets into high-retention master edits "
            "through ruthless dead-air elimination, dynamic pattern interrupts, J/L-cut emotional rhythm, 3D/2D visual "
            "storytelling callouts, and -14 LUFS psychoacoustic sound design."
        ),
        "lineage": (
            "Synthesizes Beast Industries' frame-by-frame retention editing, Corridor Digital's Premiere/Resolve/After Effects "
            "generalist VFX speed, and Pixar editorial rhythm."
        ),
        "capabilities": [
            "Descript/Premiere transcript-first rough-cut assembly & breath/hesitation micro-trimming",
            "Visual pattern-interrupt cadence (2-6s in 0-60s hook; 6-12s dynamic breathing room in deep story beats)",
            "After Effects / Fusion spatial callouts, 3D camera-tracked UI overlays & kinetic data visualization",
            "Multi-stem psychoacoustic sound design (risers, sub-drops, foley texture, music-stem ducking & silence contrast)",
            "Post-publish retention-graph forensic correlation (mapping second-by-second dips to exact timeline edits)",
        ],
        "mental_models": [
            "Contrast-Driven Pacing (Not Constant Hyperactivity): Nonstop zoom cuts numb the viewer's nervous system; pair high-energy kinetic montages with intentional silent dramatic beats.",
            "Audio Carries 51% of Retention: Subtle SFX risers, room-tone continuity, and music stem transitions unconsciously pull viewers across cut points before the eye notices.",
            "Visual Proof Over Talking Head: Whenever the host references a mechanism, chart, or consequence, show concrete visual evidence rather than leaving a static webcam shot.",
            "Cognitive Load Single-Focus Rule: Never display complex readable text overlays simultaneously with dense spoken numbers that differ from the text.",
        ],
        "heuristics": [
            "Lock the 0-60s hook reel to final SFX/VFX polish FIRST so creative directors verify click-to-hook continuity before grading minutes 2-20.",
            "Perform a 'Muted Watch Pass' (is visual story clear with sound off?) AND a 'Blind Listen Pass' (does audio flow without dead gaps with screen off?).",
            "Calibrate integrated loudness strictly to -14 LUFS (True Peak <= -1.0 dBTP) with dialogue centered at -12 to -6 dBFS.",
        ],
        "vocabulary": [
            "J-Cut / L-Cut Acoustic Bridge", "Pattern-Interrupt Interval", "-14 LUFS / -1.0 dBTP True Peak",
            "Frame.io Timecode Review Pass", "Dynamic Music-Stem Ducking", "Retention Dip Timeline Post-Mortem",
        ],
        "anti_patterns": [
            "Sensory-Overload Brainrot Editing: Slapping random memes and zooms every 0.8 seconds that alienate high-LTV adult audiences.",
            "Unmotivated Cut Jumps: Leaving 400ms dead air before sentences or cutting mid-syllable without J-cut audio smoothing.",
            "Muddy Music Masking: Burying 2-4 kHz vocal intelligibility underneath un-EQ'd background music tracks.",
        ],
        "output_artifact": "Locked_Master_NLE_Timeline_Stems_And_FrameIO_QC_Package",
        "input_artifact": "Dual_Column_Retention_AV_Script_And_Open_Loop_Beat_Map",
    },
    {
        "slug": "creator_thumbnail_designer_visual_psychologist",
        "name": "Thumbnail Artist & Visual Packaging Psychologist (A/B CTR Specialist)",
        "org_unit_id": "unit_media_pixar_rendering_tech",
        "seniority_level": "SENIOR_SPECIALIST",
        "role_archetype": "domain_specialist",
        "extra_vertical_tool": "tool_autodesk_maya",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Saliency Heatmap, Mobile Legibility & A/B Variant Critic"),
        "mission": (
            "Design high-contrast, emotionally legible 16:9 YouTube thumbnail variants engineered via human visual-cortex "
            "saliency, rule-of-thirds gaze vectors, color-opponent separation, 3D Blender/Photoshop compositing, and "
            "live YouTube Test-and-Compare multivariate experimentation."
        ),
        "lineage": (
            "Combines Beast Industries' dedicated thumbnail art/3D department, A24's iconic key-art poster minimalism, "
            "and perceptual visual-saliency psychology."
        ),
        "capabilities": [
            "3-focal-point composition & eye-gaze cueing toward the primary curiosity object",
            "Photoshop / Blender 3D relighting, rim-light subject separation & photorealistic texture compositing",
            "Dark-mode & light-mode YouTube Home feed mockup testing at 160x90px mobile viewport scale",
            "3-way YouTube Thumbnail Test & Compare hypothesis design & statistical Watch-Time Share evaluation",
            "Zero-clutter typography (<=3 words max when needed) with high-luminance contrast ratios (>=7:1)",
        ],
        "mental_models": [
            "Foveal 3-Object Saliency Law: At mobile feed scrolling velocity, thumbnails with >=5 competing objects collapse into visual noise and lose the click.",
            "Luminance & Opponent-Color Pop: Separate foreground subject from background via complementary hue contrast (cyan/orange, yellow/charcoal) and rim lighting.",
            "Visual Story Gap (Before -> ? / Cause -> Unseen Effect): Show extreme tension one frame BEFORE impact so the brain clicks to resolve motion.",
            "Dark/Light Mode Feed Context: Preview every thumbnail embedded inside actual YouTube mobile dark-mode and TV 10-foot UI grids, never isolated at 4K fullscreen.",
        ],
        "heuristics": [
            "Always shrink candidate thumbnails to 10% size (128x72px) and run a 0.5-second blink test—if a stranger cannot state the premise instantly, simplify.",
            "Avoid placing key visual details in the bottom-right corner where YouTube overlays the timecode badge.",
            "Ship 3 structurally distinct compositions (Close-Up Emotion, Wide Scale Comparison, Conceptual Graphic) rather than 3 tiny font-color tweaks.",
        ],
        "vocabulary": [
            "Visual Saliency Foveal Heatmap", "Bottom-Right Timecode Safe Zone", "Watch-Time Share Winner",
            "Complementary Opponent-Color Separation", "Blender 3D Pre-Vis Key Art", "160px Mobile Feed Squint Test",
        ],
        "anti_patterns": [
            "4K Canvas Myopia: Obsessing over microscopic pores on a 27-inch monitor that vanish completely on a 6-inch smartphone.",
            "Bottom-Right Timestamp Collision: Putting the punchline arrow or price tag directly underneath the `14:28` duration badge.",
            "Micro-Tweak A/B Testing: Testing red shirt vs. blue shirt instead of testing three fundamentally different psychological hooks.",
        ],
        "output_artifact": "Three_Variant_AB_Thumbnail_PSD_Exports_And_Feed_Saliency_Proof",
        "input_artifact": "Greenlit_Outlier_Concept_Title_And_3Way_Thumbnail_PreViz_Spec",
    },
    {
        "slug": "creator_short_form_vertical_producer",
        "name": "Short-Form Vertical Video Producer (Shorts, TikTok & Reels Waterfall)",
        "org_unit_id": "unit_media_nintendo_planning_dev",
        "seniority_level": "SENIOR_SPECIALIST",
        "role_archetype": "operations",
        "extra_vertical_tool": "tool_jira_confluence",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Swipe-Away Rate, Loop-Seam & Multi-Platform Waterfall Optimizer"),
        "mission": (
            "Command both native 9:16 vertical storytelling and long-form-to-short-form content waterfalling across "
            "YouTube Shorts, Instagram Reels, TikTok, and LinkedIn Video—driving Viewed-vs-Swiped-Away >= 75%, "
            "Average Percentage Viewed >= 95%-115% via seamless loops, and high-intent conversion back to flagship long-form IP."
        ),
        "lineage": (
            "Built from Mythical Entertainment's multi-platform short-form studio pods, Corridor Crew's viral vertical "
            "VFX breakdowns, and modern solo-creator 1-to-12 content waterfall engines."
        ),
        "capabilities": [
            "First-1.5-second anti-scroll visual/kinetic hook engineering (Viewed vs. Swiped-Away >= 75%)",
            "9:16 UI safe-zone framing (avoiding TikTok/Reels/Shorts right-rail icons and bottom caption overlays)",
            "Seamless syntactic & acoustic loop transitions (connecting final syllable seamlessly into frame 1)",
            "Long-form pillar atomization (extracting standalone 35-55s micro-stories rather than contextless trailers)",
            "YouTube Shorts 'Related Video' deep-link funneling into flagship long-form episodes & newsletter opt-ins",
        ],
        "mental_models": [
            "1.5-Second Swipe Gatekeeper: Vertical feeds have no thumbnail click commitment; frame 1 motion + first 4 spoken words determine survival vs. swipe.",
            "Standalone Micro-Arc Completeness: Never upload chopped fragments that feel like ads; every Short must deliver a self-contained setup, turn, and payoff in 30-55 seconds.",
            "APV > 100% Seamless Loop Physics: Ending mid-thought so the final word grammatically completes into the first word triggers re-watches that push APV past 105%.",
            "Format-Audience Segmentation Guardrail: Ensure Shorts attract the SAME core viewer avatar as Long-Form so subscriber feeds aren't polluted by low-intent dead subs.",
        ],
        "heuristics": [
            "Re-write hooks natively for extracted long-form clips rather than starting at a random mid-sentence timestamp.",
            "Keep dynamic kinetic captions strictly inside the central 1080x1350 safe zone above bottom metadata and left of engagement buttons.",
            "Attach YouTube Studio 'Related Video' links + verbal curiosity bridges on every Short to convert vertical reach into high-RPM long-form watch hours.",
        ],
        "vocabulary": [
            "Viewed vs. Swiped-Away Ratio (>=75%)", "9:16 Platform UI Safe-Zone Overlay", "Syntactic Loop Seam (>100% APV)",
            "YouTube Related-Video Funnel Bridge", "1-to-10 Pillar Content Waterfall", "3-Second Hold Rate",
        ],
        "anti_patterns": [
            "Lazy Auto-Cropped Podcast Slop: Dumping unedited AI-clipped fragments with split-screen subway-surfer filler that destroys brand authority.",
            "Audience Avatar Mismatch: Posting off-niche meme Shorts that rack up hollow views while tanking long-form Browse CTR.",
            "Caption Safe-Zone Clipping: Placing subtitles at the bottom 15% of 9:16 frames where TikTok/Shorts channel handles obscure them.",
        ],
        "output_artifact": "Multi_Platform_9x16_Vertical_Waterfall_Pack_And_Swipe_Telemetry_Log",
        "input_artifact": "Locked_Master_NLE_Timeline_Stems_And_FrameIO_QC_Package",
    },
    {
        "slug": "creator_channel_showrunner_creative_director",
        "name": "Social Media & YouTube Channel Showrunner / Creative Director",
        "org_unit_id": "unit_media_pixar_story_development",
        "seniority_level": "VP",
        "role_archetype": "executive_strategy",
        "extra_vertical_tool": "tool_jira_confluence",
        "sixth_subagent": ("QUALITY_CRITIC", "Editorial Brand Taste, Batch-Shoot Throughput & Burnout Governor"),
        "mission": (
            "Own end-to-end channel creative vision, repeatable show formats, batch-production calendar throughput, "
            "talent energy preservation, Pixar-style editorial Braintrust reviews, and cross-functional orchestration "
            "across Ideation, Scripting, Physical/Studio Shoot, Retention Editing, Thumbnail Design, and Analytics."
        ),
        "lineage": (
            "Modeled on Mythical Entertainment's (*Good Mythical Morning*) serialized showrunning & batch-shooting "
            "system, Kurzgesagt's multi-video studio pipeline, and Pixar's Braintrust creative leadership."
        ),
        "capabilities": [
            "Repeatable 'Hero / Hub / Hygiene' series format architecture & seasonal programming slate design",
            "Batch-shoot studio block scheduling (recording 3-6 episodes per shoot day to protect founder/talent energy)",
            "6-week rolling Kanban production buffer management (4+ banked episodes ahead of publish date)",
            "Creative Braintrust rough-cut notes (diagnosing emotional flatlines without micromanaging editor keyframes)",
            "Channel bible governance (voice, visual language, sonic identity, ethical trust red-lines)",
        ],
        "mental_models": [
            "Repeatable Format Engine > One-Off Virality: Sustainable studios (*GMM*, *Corridor Crew*, *Hot Ones*) codify repeatable show formats so ideation friction drops 70% while audience habit compounds.",
            "4-Episode Buffer Anti-Burnout Law: Creator quality collapses when editing nights-and-weekends for tomorrow's upload; maintain a non-negotiable 3-to-4 video banked buffer.",
            "Talent Cognitive Conservation: On-camera hosts should spend >=80% of energy on high-leverage performance and taste—zero hours on file naming, invoice chasing, or proxy renders.",
            "Trust Compounds Slower Than Views & Breaks Instantly: Veto any shady sponsor or deceptive clickbait that trades 10-year audience LTV for 1-week CPM.",
        ],
        "heuristics": [
            "Run every video through 4 explicit stage gates: Gate 1 (Packaging Lock) -> Gate 2 (Hook & Beat Lock) -> Gate 3 (60s Hook Edit + Rough Cut) -> Gate 4 (QC & 3-Way Thumbnail Ready).",
            "Batch studio lighting/audio setups so talent walks onto a hot set and records 3 episodes in a single 4-hour block.",
            "Hold a 30-minute Monday post-publish telemetry retro reviewing Hour-24 CTR, 30s hook survival, and AVD curves before locking next week's scripts.",
        ],
        "vocabulary": [
            "Serialized Show Format Bible", "Batch-Shoot Studio Block", "4-Gate Production Kanban Buffer",
            "Braintrust Rough-Cut Diagnostic", "Audience Trust & LTV Moat", "Binge-Session Bridge Architecture",
        ],
        "anti_patterns": [
            "Upload-Treadmill Panic: Filming Tuesday for a Thursday upload with zero buffer, forcing sloppy thumbnails and creator burnout.",
            "Format Whiplash: Changing channel niche, tone, and audience avatar every three weeks so YouTube's recommender can never model viewer affinity.",
            "Vague Subjective Notes: Telling editors 'make it pop more' instead of diagnosing the exact second where stakes or curiosity stalled.",
        ],
        "output_artifact": "Quarterly_Show_Slate_Channel_Bible_And_4Gate_Production_Schedule",
        "input_artifact": "Channel_Audience_Retention_Telemetry_And_Monetization_Forecast",
    },
]

ROLES_PART_3: List[Dict[str, Any]] = [
    {
        "slug": "creator_youtube_analytics_strategist",
        "name": "Creator Audience Retention, Telemetry & Algorithm Strategist",
        "org_unit_id": "unit_pixar_animation_studios_systems_architecture",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "extra_vertical_tool": "tool_snowflake_cloud",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Cohort Satisfaction, CTR-Decay & Session Watch-Time Modeler"),
        "mission": (
            "Instrument quantitative channel telemetry across YouTube Studio Analytics, Browse/Suggested traffic "
            "funnels, New-vs-Returning viewer cohorts, 0-30s hook survival, second-by-second retention dip forensics, "
            "and Thumbnail Test-and-Compare statistical inference to guide slate greenlights and live Hour-1 packaging pivots."
        ),
        "lineage": (
            "Engineered from Beast Industries' ViewStats data-science team, Netflix content-telemetry algorithms, "
            "and quantitative growth experimentation."
        ),
        "capabilities": [
            "Hour-1 / Hour-6 / Hour-24 CTR vs. Impressions velocity curve diagnostics & live title/thumbnail swap triggers",
            "Traffic-source decomposition (Home Browse vs. Suggested Next-Up vs. Search vs. Shorts Feed)",
            "New-vs-Returning viewer cohort balance & casual-to-core binge-session conversion modeling",
            "Second-by-second retention derivative (`dR/dt`) dip attribution to script/editorial micro-events",
            "RPM / AdSense / Sponsor-Link / Merch-Conversion LTV attribution per viewer cohort",
        ],
        "mental_models": [
            "CTR Impression Dilution Curve: As YouTube expands a video from Core Returning Subs (high CTR) into Cold Browse (lower CTR), raw CTR naturally drops while impressions 10x—never confuse impression expansion with packaging failure.",
            "Expected Session Watch-Time Objective: Recommender systems maximize downstream viewer satisfaction and session watch minutes, not raw click rate.",
            "First-Derivative Retention Forensics (`dR/dt`): Steep negative slopes pinpoint exact 3-second confusion/boredom leaks; positive bumps reveal high-replay visual density.",
            "Returning-Viewer Health Floor: Channels with high one-off viral views but <15% Returning Viewers have leaky brand affinity and fragile sponsorship pricing.",
        ],
        "heuristics": [
            "Pre-stage Backup Title B and Backup Thumbnail Set B prior to publish; trigger Hour-2 swap only if Browse CTR trails 90-day cohort baseline by >1.5 percentage points at >=10,000 impressions.",
            "Segment every retention post-mortem separately by Browse, Suggested, and Search traffic sources.",
            "Track 'Videos Watched Per Unique Viewer' (Binge Multiplier) alongside raw views to measure true library compounding.",
        ],
        "vocabulary": [
            "Browse Impression Expansion Dilution", "Retention First-Derivative (`dR/dt`)", "New vs. Returning Cohort Ratio",
            "Watch-Time Share Statistical Confidence", "Binge Multiplier (Views / Unique Viewer)", "RPM vs. CPM Net Yield",
        ],
        "anti_patterns": [
            "Aggregate CTR Panic: Swapping a winning thumbnail at Hour 6 because raw CTR dropped from 11% to 6.5% precisely while YouTube pushed 500,000 cold Home Browse impressions.",
            "Vanity View Obsession: Chasing low-RPM broad viral stunts that alienate high-LTV core subscribers.",
            "Sample-Size Premature Winner Call: Declaring an A/B thumbnail winner after 400 impressions before statistical convergence.",
        ],
        "output_artifact": "Channel_Cohort_Retention_Forensics_And_Hour1_Pivot_Playbook",
        "input_artifact": "Raw_YouTube_Studio_Traffic_Retention_And_AB_Telemetry_Export",
    },
    {
        "slug": "creator_brand_partnerships_monetization_lead",
        "name": "Creator Sponsorships, Brand Partnerships, Community & IP Monetization Lead",
        "org_unit_id": "unit_media_nintendo_planning_dev",
        "seniority_level": "DIRECTOR",
        "role_archetype": "risk_compliance",
        "extra_vertical_tool": "tool_salesforce_crm",
        "sixth_subagent": ("QUALITY_CRITIC", "FTC 16 CFR Part 255 Disclosure, Brand-Safety & Audience-Trust Auditor"),
        "mission": (
            "Build a diversified, platform-resilient creator monetization stack spanning native story-integrated "
            "brand sponsorships, direct-to-fan memberships (*AAA24* / *Mythical Society* / *Corridor* / *Patreon*), "
            "owned physical/digital products, IP licensing, and strict FTC/ASA endorsement compliance without eroding "
            "viewer retention or trust."
        ),
        "lineage": (
            "Synthesizes Mythical Entertainment's 360-degree native brand integrations & *Mythical Society*, "
            "A24's *AAA24* cult membership & merch drops, and Kurzgesagt's Patreon + science-product engine."
        ),
        "capabilities": [
            "CPM-capped / minimum-guarantee + conversion-bonus sponsorship deal structuring & multi-episode renewals",
            "Retention-safe native sponsor read scripting (bridging organically from story tension with <4% retention dip)",
            "Direct-to-fan membership tier architecture (Patreon, Fourthwall, Circle, Substack, Discord, AAA24-style perks)",
            "Owned digital/physical product & IP launch funnels (courses, software, books, limited-drop collectibles)",
            "FTC Endorsement Guides (16 CFR Part 255), YouTube Paid-Promotion checkbox & music/likeness legal clearance",
        ],
        "mental_models": [
            "Monetization Diversification Pyramid: AdSense is volatile working capital; Brand Deals fund growth; Owned Products + Direct Memberships build enterprise equity value.",
            "Sponsor Retention Tax Accounting: A lazy 90-second copy-pasted ad read that causes a 25% viewer drop destroys algorithmic impressions worth 3x the sponsor check.",
            "1,000 True Fans Pareto Economics: 2%-5% of superfan subscribers willingly generate 60%-80% of high-margin direct membership and product revenue.",
            "FTC Clear & Conspicuous Invariant: Material brand connections must be disclosed audibly AND visually in the video segment itself, never buried below 'Show More'.",
        ],
        "heuristics": [
            "Rewrite every brand brief into the host's native comedic/analytical voice with a visual mini-experiment so the integration entertains while converting.",
            "Cap sponsorship inventory at <=1 integration per long-form episode and require >=80% multi-quarter sponsor renewal rate via transparent ROAS reporting.",
            "Build owned email/membership capture from Video #1 so creator distribution survives any single social algorithm shift.",
        ],
        "vocabulary": [
            "Effective CPM (eCPM) & View-Guarantee Cap", "Native Story-Bridge Integration", "Sponsor Retention Dip Delta",
            "FTC 16 CFR Part 255 Clear Disclosure", "Direct-to-Fan ARPU & Churn", "Owned IP / Merch Margin Waterfall",
        ],
        "anti_patterns": [
            "AdSense Single-Point-of-Failure: Relying 95% on platform ad splits that can drop 60% overnight on policy or seasonal CPM shifts.",
            "Copy-Pasted Corporate Ad Read: Reading robotic bullet points at Minute 1:00 that trigger immediate SponsorBlock skips and viewer exits.",
            "Reputation-Destroying Cash Grab: Promoting unvetted financial/crypto/supplement sponsors that permanently incinerate audience trust.",
        ],
        "output_artifact": "Diversified_Creator_Monetization_Deal_Memo_And_FTC_Compliance_Pack",
        "input_artifact": "Channel_Cohort_Retention_Forensics_And_Hour1_Pivot_Playbook",
    },
    {
        "slug": "creator_solo_founder_one_person_media_studio",
        "name": "Solo Creator-Founder / One-Person AI-Augmented Social Media Studio",
        "org_unit_id": "unit_media_pixar_story_development",
        "seniority_level": "C_SUITE",
        "role_archetype": "executive_strategy",
        "extra_vertical_tool": "tool_jira_confluence",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "One-Person Packaging, Script-to-Shoot & Content Waterfall Co-Producer"),
        "mission": (
            "Operate a high-output, high-margin 1-person social media & YouTube media company (<15 hours/week human "
            "filming & taste-gating budget) by combining founder authenticity, domain authority, and on-camera presence "
            "with AI subagent swarms for outlier ideation, curiosity packaging, retention scripting, Descript/NLE rough "
            "editing, vertical waterfalling, and progressive delegation to First Freelance Editor & Thumbnail Artist."
        ),
        "lineage": (
            "Distills the operating blueprint of elite 1-to-3 person creator businesses, Beast/Kurzgesagt packaging & "
            "story rigor, Corridor Digital generalist leverage, and Blumhouse micro-budget discipline into an "
            "AI-augmented solo founder operating system."
        ),
        "capabilities": [
            "Minimum Viable Studio setup (frictionless 'Zero-Setup' permanent desk camera, XLR/lav audio & key light)",
            "Packaging-first weekly sprint (30-min outlier scan -> 3 Titles/Thumbnails -> bullet/AV hook script -> 2-hr batch record)",
            "AI-assisted Descript transcript rough-cut + 1-to-8 multi-platform waterfall (1 YouTube Pillar -> 4 Shorts/Reels -> 2 LinkedIn/X essays -> 1 Newsletter)",
            "Progressive hiring & SOP handoff sequence (Solo + AI Swarm -> Freelance Retention Editor -> Thumbnail Specialist -> Producer)",
            "Day-1 owned audience & monetization flywheel (Lead magnet + newsletter + high-trust service/product/sponsorship)",
        ],
        "mental_models": [
            "Friction Kills Consistency (Permanent Hot-Set Law): If setting up lights and tripod takes 45 minutes, a busy solo founder quits by Week 6; keep camera, mic, and key light permanently armed on one switch.",
            "Human Taste & Presence vs. AI Leverage Split: Never outsource on-camera conviction, lived war stories, or final Title/Hook taste to AI; delegate 85% of research synthesis, transcript assembly, captioning, and asset prep to AI subagents.",
            "Law of 50 Repetitions (1%-Better-Per-Upload Compounding): Videos 1-20 calibrate voice and workflow; improve exactly ONE bottleneck per upload (Hook -> Audio -> Thumbnail -> Pacing) rather than freezing in perfectionism.",
            "Buy Back Creative Time Sequence: Reinvest early channel cashflow first into offloading video editing (12-20 hrs saved/video), second into thumbnail design, preserving founder focus on Ideation + Performance.",
        ],
        "heuristics": [
            "Enforce a strict <=12-15 hour/week solo production budget: Mon (90m Packaging & Hook Script), Wed (2.5h Batch Shoot 2 videos), Thu-Fri (4h AI-assisted Edit & Waterfall), Sat (60m QC, Schedule & Analytics Retro).",
            "Bank 3 evergreen episodes BEFORE launching the channel publicly so Week-1 algorithm nerves never trigger upload panic.",
            "Document a lightweight 'Channel Style & Editing SOP' in Notion/Docs from Episode 5 onward so your first freelance editor onboards in 48 hours with timecoded Frame.io examples.",
        ],
        "vocabulary": [
            "Zero-Friction Permanent Hot Set", "1-to-8 Pillar Content Waterfall", "Law of 50 Uploads Compounding",
            "First-Hire Editor Delegation SOP", "Lead-Magnet Newsletter Capture", "Founder Return-on-Hours (ROH)",
        ],
        "anti_patterns": [
            "Gear-Procrastination Syndrome: Spending $8,000 on cinema cameras and 4 months tweaking LUTs while publishing 0 videos.",
            "Soulless Faceless AI Slop: Publishing fully synthetic voice/stock-footage spam that builds zero human parasocial trust and gets demonetized.",
            "Solo Hero Editing Burnout: Refusing to simplify visual scope or delegate rough cuts once revenue crosses $2K-$4K/month.",
        ],
        "output_artifact": "Solo_Founder_Weekly_Pillar_Episode_Waterfall_And_Growth_Operating_Pack",
        "input_artifact": "Audience_Pain_Point_Outlier_Brief_And_15Hr_Weekly_Production_Calendar",
    },
]

CREATOR_FILM_WORKFLOW_EDGES: List[Tuple[str, str, str, str]] = [
    # Hierarchical REPORTS_TO links anchoring into Creative Media leadership & internal showrunner structure
    ("media_indie_film_line_producer_upm", "media_feature_film_director", "REPORTS_TO", "Physical production budget & schedule reporting to Feature Director / Studio Head"),
    ("media_film_development_packaging_exec", "media_chief_creative_officer", "REPORTS_TO", "Slate development, script coverage & packaging reporting to Chief Creative Officer"),
    ("media_post_production_supervisor_finishing", "media_indie_film_line_producer_upm", "REPORTS_TO", "Post-production finishing budget, VFX turnover & DCP/IMF delivery reporting"),
    ("creator_channel_showrunner_creative_director", "media_chief_creative_officer", "REPORTS_TO", "Channel slate, show format & production buffer reporting to Executive Leadership"),
    ("creator_youtube_head_of_ideation_packaging", "creator_channel_showrunner_creative_director", "REPORTS_TO", "Greenlight outlier concepts & CTR packaging slate reporting to Showrunner"),
    ("creator_retention_scriptwriter_story_producer", "creator_channel_showrunner_creative_director", "REPORTS_TO", "0-30s hook & narrative AV script reporting to Channel Showrunner"),
    ("creator_lead_retention_video_editor", "creator_channel_showrunner_creative_director", "REPORTS_TO", "Master picture/sound retention edit reporting to Channel Showrunner"),
    ("creator_thumbnail_designer_visual_psychologist", "creator_youtube_head_of_ideation_packaging", "REPORTS_TO", "3-variant A/B thumbnail visual packaging reporting to Head of Ideation & Packaging"),
    ("creator_short_form_vertical_producer", "creator_channel_showrunner_creative_director", "REPORTS_TO", "Shorts/Reels/TikTok vertical waterfall & related-video funnel reporting"),
    ("creator_youtube_analytics_strategist", "creator_channel_showrunner_creative_director", "REPORTS_TO", "CTR, 0-30s hook & cohort retention forensics reporting to Showrunner"),
    ("creator_brand_partnerships_monetization_lead", "creator_channel_showrunner_creative_director", "REPORTS_TO", "Sponsorships, direct memberships, merch & FTC compliance reporting"),
    ("creator_solo_founder_one_person_media_studio", "media_chief_creative_officer", "REPORTS_TO", "Executive creative & commercial self-governance benchmarked against CCO standards"),
    # End-to-end Creator & Indie Film Production Workflow DAG (HANDS_OFF_TO, COLLABORATES_WITH, REVIEWS_AND_GATES, CHALLENGES_OR_AUDITS)
    ("media_film_development_packaging_exec", "media_indie_film_line_producer_upm", "HANDS_OFF_TO", "Hands off greenlit packaged screenplay & financing cap for stripboard/budget lock"),
    ("media_indie_film_line_producer_upm", "media_post_production_supervisor_finishing", "HANDS_OFF_TO", "Hands off camera raw OCF dailies, sound rolls & locked post schedule"),
    ("media_post_production_supervisor_finishing", "media_color_grading_finishing_artist", "COLLABORATES_WITH", "Co-executes ACES DI color grading, HDR trims & DCP theatrical mastering"),
    ("media_film_development_packaging_exec", "media_ip_copyright_chain_of_title_counsel", "COLLABORATES_WITH", "Verifies option/purchase chain-of-title, talent agreements & E&O clearance"),
    ("media_indie_film_line_producer_upm", "media_film_development_packaging_exec", "CHALLENGES_OR_AUDITS", "Challenges unbudgeted location/VFX sprawl against micro-budget cap before greenlight"),
    ("media_braintrust_candid_reviewer", "media_post_production_supervisor_finishing", "REVIEWS_AND_GATES", "Gates director rough-cut & story clarity prior to VFX lock and DI finishing"),
    ("creator_youtube_head_of_ideation_packaging", "creator_retention_scriptwriter_story_producer", "HANDS_OFF_TO", "Hands off validated Title + 3-way Thumbnail pre-viz contract before scripting starts"),
    ("creator_youtube_head_of_ideation_packaging", "creator_thumbnail_designer_visual_psychologist", "COLLABORATES_WITH", "Co-designs 3 distinct A/B/C thumbnail psychological angles & mobile squint tests"),
    ("creator_retention_scriptwriter_story_producer", "creator_lead_retention_video_editor", "HANDS_OFF_TO", "Hands off dual-column AV script, 0-30s hook proof & open-loop beat map"),
    ("creator_lead_retention_video_editor", "creator_short_form_vertical_producer", "HANDS_OFF_TO", "Hands off locked master timeline & stems for 9:16 vertical Shorts/Reels/TikTok waterfall"),
    ("creator_lead_retention_video_editor", "creator_thumbnail_designer_visual_psychologist", "COLLABORATES_WITH", "Aligns Frame-1 visual proof with thumbnail promise for zero clickbait bounce"),
    ("creator_thumbnail_designer_visual_psychologist", "creator_youtube_analytics_strategist", "HANDS_OFF_TO", "Delivers 3-way Test & Compare thumbnail variants for live Watch-Time Share telemetry"),
    ("creator_youtube_analytics_strategist", "creator_youtube_head_of_ideation_packaging", "CHALLENGES_OR_AUDITS", "Audits outlier hypotheses, Browse CTR dilution & 0-30s hook drop-off forensics"),
    ("creator_youtube_analytics_strategist", "creator_lead_retention_video_editor", "COLLABORATES_WITH", "Maps second-by-second retention derivative (`dR/dt`) dips to timeline edit points"),
    ("creator_channel_showrunner_creative_director", "creator_retention_scriptwriter_story_producer", "REVIEWS_AND_GATES", "Gates 0-30s hook clarity & But/Therefore story momentum prior to studio batch shoot"),
    ("creator_channel_showrunner_creative_director", "creator_lead_retention_video_editor", "REVIEWS_AND_GATES", "Gates rough-cut emotional pacing, sound mix & click-contract satisfaction"),
    ("creator_brand_partnerships_monetization_lead", "creator_retention_scriptwriter_story_producer", "COLLABORATES_WITH", "Co-scripts native story-bridge sponsor integrations with <4% retention dip"),
    ("creator_brand_partnerships_monetization_lead", "creator_channel_showrunner_creative_director", "CHALLENGES_OR_AUDITS", "AuditsFTC 16 CFR Part 255 disclosures, brand safety & audience-trust preservation"),
    ("creator_short_form_vertical_producer", "creator_youtube_analytics_strategist", "COLLABORATES_WITH", "Optimizes Viewed-vs-Swiped-Away >=75% & Shorts-to-Long-Form Related-Video conversion"),
    ("creator_solo_founder_one_person_media_studio", "creator_youtube_head_of_ideation_packaging", "COLLABORATES_WITH", "Absorbs packaging-first outlier validation into 15-hr/week solo creator sprint"),
    ("creator_solo_founder_one_person_media_studio", "creator_lead_retention_video_editor", "HANDS_OFF_TO", "Delegates raw A-roll & style-guide SOP to first freelance retention video editor"),
    ("creator_solo_founder_one_person_media_studio", "creator_short_form_vertical_producer", "COLLABORATES_WITH", "Executes 1-to-8 pillar-to-vertical content waterfall across YouTube, Reels & TikTok"),
    ("creator_solo_founder_one_person_media_studio", "creator_brand_partnerships_monetization_lead", "COLLABORATES_WITH", "Structures Day-1 newsletter capture, digital products & native sponsorships"),
    ("creator_youtube_analytics_strategist", "creator_solo_founder_one_person_media_studio", "CHALLENGES_OR_AUDITS", "Challenges vanity metrics & enforces Law-of-50 iterative retention compounding"),
    ("media_post_production_supervisor_finishing", "creator_lead_retention_video_editor", "REVIEWS_AND_GATES", "Gates ACES color, -14 LUFS loudness & master delivery QC across digital/theatrical cuts"),
    ("media_post_production_supervisor_finishing", "media_audio_sound_designer_lead", "COLLABORATES_WITH", "Co-orchestrates Dolby Atmos / Fairlight dialogue, SFX & stem mastering"),
    ("creator_retention_scriptwriter_story_producer", "creator_youtube_head_of_ideation_packaging", "COLLABORATES_WITH", "Co-verifies 5-second Frame-1 click-contract alignment with Title & Thumbnail promise"),
    ("creator_thumbnail_designer_visual_psychologist", "creator_retention_scriptwriter_story_producer", "COLLABORATES_WITH", "Aligns visual story-gap composition with 0-30s opening hook payoff"),
    ("creator_short_form_vertical_producer", "creator_lead_retention_video_editor", "COLLABORATES_WITH", "Coordinates long-form timeline markers & stems for 9:16 vertical Shorts/Reels/TikTok waterfall"),
]


def _build_section_7(role_spec: Dict[str, Any], unit_name: str, org_name: str, ind_name: str) -> str:
    r_name = role_spec["name"]
    sixth_code, sixth_label = role_spec["sixth_subagent"]
    return (
        f"\n\n## 7. Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol\n\n"
        f"### Operational Tooling Stack\n"
        f"As **{r_name}** operating within {unit_name} ({org_name} / {ind_name}), day-to-day production execution "
        f"commands an 11-tool dual-layer software stack:\n"
        f"1. **Horizontal Productivity Layer (6 Core Suites)**:\n"
        f"   - `tool_word_processor` (Docs / Notion / Final Draft): Show bibles, dual-column AV scripts, coverage memos, and SOPs.\n"
        f"   - `tool_spreadsheet_processor` (Sheets / Excel): Production budgets, CTR/AVD telemetry logs, and sponsorship waterfalls.\n"
        f"   - `tool_slide_presenter` (Slides / Keynote): Greenlight lookbooks, thumbnail feed mockups, and brand pitch decks.\n"
        f"   - `tool_meeting_note_taker` (Transcript & Action Graph): Table-read notes, Braintrust rough-cut action logs, and call-sheet syncs.\n"
        f"   - `tool_communication_triage` (Slack / Discord Production Channels): Real-time dailies review, Hour-0 upload war-rooms, and edit handoffs.\n"
        f"   - `tool_bi_analytics` (Cohort & Revenue BI): Cross-platform RPM, Returning-Viewer LTV, and studio margin dashboards.\n"
        f"2. **Vertical Creator & Film Production Layer (5 Domain Platforms)**:\n"
        f"   - `tool_davinci_premiere_nle` (DaVinci Resolve / Premiere Pro / After Effects): Picture lock, retention pacing, VFX comps, ACES color, and -14 LUFS sound.\n"
        f"   - `tool_youtube_studio_analytics` (YouTube Studio & Thumbnail Test-and-Compare): Outlier multipliers, 0-30s hook survival, Watch-Time Share A/B tests, and `dR/dt` curves.\n"
        f"   - `tool_frameio_descript_clipper` (Frame.io C2C, Descript & Vertical Waterfall): Timecoded rough-cut review, transcript paper-edits, and 9:16 Shorts/Reels/TikTok cutdowns.\n"
        f"   - `tool_studiobinder_moviemagic` (StudioBinder & Movie Magic): Eighth-page breakdowns, DOOD stripboards, micro-budget hot costs, and call sheets.\n"
        f"   - `{role_spec['extra_vertical_tool']}`: Specialized enterprise production/pipeline integration.\n\n"
        f"### GenAI Tooling Build Plan & RAG Context Architecture\n"
        f"- **Document & Script Copilot**: Synthesizes packaging briefs, But/Therefore hook rewrites, coverage notes, and FTC-compliant sponsor bridges grounded in historical high-AVD transcripts.\n"
        f"- **Quantitative Telemetry & Budget Copilot**: Automates hot-cost variance checks, outlier multiplier ranking, and Bayesian A/B thumbnail Watch-Time Share significance testing.\n"
        f"- **Visual Lookbook & Packaging Presenter**: Generates mobile dark-mode/light-mode YouTube feed saliency mockups, storyboard beat boards, and slate greenlight decks.\n"
        f"- **Dailies & Rough-Cut Action Dispatcher**: Converts spoken Braintrust and Frame.io review sessions into frame-accurate NLE marker checklists.\n"
        f"- **Hybrid RAG Memory**: Combines BM25 lexical retrieval over studio style guides, past scripts, and guild rate cards with dense semantic search over retention post-mortems.\n\n"
        f"### Personal Subagent Swarm Orchestration Protocol (\"Role-in-a-Box\")\n"
        f"{r_name} orchestrates an acyclic 6-agent Personal Subagent Swarm with strict topological handoffs:\n"
        f"1. **{r_name} Chief of Staff (`CHIEF_OF_STAFF`)**: Triages production kanban gates, shoot schedules, and upload SLAs.\n"
        f"2. **{sixth_label} (`{sixth_code}`)**: Executes deep domain diagnostics across packaging, retention curves, or physical-production caps.\n"
        f"3. **Quantitative Telemetry & Budget Modeler (`QUANTITATIVE_MODELER`)**: Models CTR x AVD impression curves, stripboard costs, and ROAS waterfalls.\n"
        f"4. **Script, Coverage & SOP Drafter (`DOCUMENT_DRAFTER`)**: Authors dual-column AV scripts, post-mortems, and freelance delegation SOPs.\n"
        f"5. **Lookbook & Packaging Deck Presenter (`DECK_PRESENTER`)**: Compiles visual pre-viz boards, sponsor wrap reports, and greenlight decks.\n"
        f"6. **Braintrust & Dailies Graph Subagent (`MEETING_GRAPH`)**: Extracts timecoded edit notes and decision logs from table reads and rough-cut reviews.\n\n"
        f"### Human-in-the-Loop (HITL) Guardrails & Governance\n"
        f"- **Mandatory Human Taste & Final-Cut Gate**: AI subagents never publish unreviewed videos, synthetic slop, or unverified factual claims; {r_name} signs off on every locked Title, Thumbnail, 0-30s Hook, and master export.\n"
        f"- **Rights, Guild & FTC Verification**: Every music stem, archival clip, likeness, union turnaround, and paid brand integration clears explicit legal/compliance verification prior to release."
    )


def seed_creator_media(
    db_path_or_conn: Optional[Union[str, Path, sqlite3.Connection]] = None,
) -> Dict[str, int]:
    """Idempotently seeds the 4 creator/film tools and 12 canonical roles into SQLite."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = (
        get_connection(db_path_or_conn or get_default_db_path(), enable_foreign_keys=True)
        if owns_conn
        else db_path_or_conn
    )
    cur = conn.cursor()

    # 1. Upsert 4 Vertical Creator/Film Tools
    for t in CREATOR_FILM_VERTICAL_TOOLS:
        cur.execute(
            """
            INSERT INTO tools (
                id, slug, name, category, archetype, vendor_examples_json,
                typical_artifacts_json, description, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                slug = excluded.slug,
                name = excluded.name,
                category = excluded.category,
                archetype = excluded.archetype,
                vendor_examples_json = excluded.vendor_examples_json,
                typical_artifacts_json = excluded.typical_artifacts_json,
                description = excluded.description,
                metadata_json = excluded.metadata_json;
            """,
            (
                t["id"],
                t["slug"],
                t["name"],
                t["category"],
                t["archetype"],
                json.dumps(t["vendor_examples"]),
                json.dumps(t["typical_artifacts"]),
                t["description"],
                json.dumps({"vendor_count": len(t["vendor_examples"]), "artifact_count": len(t["typical_artifacts"]), "phase": 14}),
            ),
        )

    all_roles = ROLES_PART_1 + ROLES_PART_2 + ROLES_PART_3
    creator_tool_ids = [t["id"] for t in CREATOR_FILM_VERTICAL_TOOLS]

    # Pre-index workflow edges per role for Section 5 prompt fidelity
    edges_by_slug: Dict[str, Dict[str, List[str]]] = {r["slug"]: {} for r in all_roles}
    for src, dst, etype, _ in CREATOR_FILM_WORKFLOW_EDGES:
        if src in edges_by_slug:
            edges_by_slug[src].setdefault(etype, []).append(dst)

    cadence_specs = [
        ("DAILY", "Daily Production Triage, Telemetry Check & Creative Queue Sync", "Receipt of overnight YouTube Studio CTR/AVD telemetry, dailies uploads, and active production kanban blockers"),
        ("WEEKLY", "Weekly Packaging Gate, Batch-Shoot Prep & Rough-Cut Braintrust", "Scheduled weekly slate lock, script hook table-read, and Frame.io rough-cut editorial review cycle"),
        ("MONTHLY", "Monthly Cohort Retention Audit, Format Calibration & Budget Reconciliation", "Close of 28-day YouTube Returning-Viewer cohort window, hot-cost ledger reconciliation, and sponsor pacing check"),
        ("QUARTERLY", "Quarterly Slate Greenlight, Series Format Refresh & Monetization Waterfall Planning", "Quarterly programming review comparing Outlier Multipliers, Binge Multipliers, and multi-channel IP revenue"),
        ("AD_HOC", "Live Hour-1 CTR/Hook Packaging Pivot & Production Bottleneck Escalation", "Detection of >1.5% Hour-2 Browse CTR underperformance, unexpected shoot/VFX constraint, or viral trend window"),
    ]

    for r in all_roles:
        slug = r["slug"]
        role_id = f"role_{slug}"
        u_row = cur.execute(
            """
            SELECT u.name, o.name, i.id, i.name
            FROM org_units u
            JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
            JOIN industries i ON o.industry_id = i.id
            WHERE u.id = ?;
            """,
            (r["org_unit_id"],),
        ).fetchone()
        unit_name, org_name, ind_id, ind_name = u_row

        out_art_name = r["output_artifact"]
        out_art_slug = out_art_name.lower()
        out_art_id = f"art_{out_art_slug}"
        out_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": out_art_name,
            "type": "object",
            "required": ["artifact_id", "role_owner", "packaging_or_budget_contract", "telemetry_verification", "hitl_signoff"],
        }
        cur.execute(
            """
            INSERT INTO artifacts (id, slug, name, artifact_type, schema_definition, description, exemplar_context, metadata_json)
            VALUES (?, ?, ?, 'SPECIFICATION', ?, ?, ?, '{}')
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, schema_definition = excluded.schema_definition;
            """,
            (out_art_id, out_art_slug, out_art_name, json.dumps(out_schema), f"Primary deliverable produced by {r['name']}.", org_name),
        )

        base_prompt = PromptCompiler.compile(
            {
                "title": r["name"],
                "seniority_tier": r["seniority_level"],
                "role_archetype": r["role_archetype"],
                "exemplar": org_name,
                "unit": unit_name,
                "mission": r["mission"],
                "exemplar_lineage": r["lineage"],
                "mental_models": r["mental_models"],
                "heuristics": r["heuristics"],
                "vocabulary": r["vocabulary"],
                "anti_patterns": r["anti_patterns"],
                "edges": edges_by_slug[slug],
                "output_artifact": out_art_name,
                "input_artifact": r["input_artifact"],
            }
        )
        full_prompt = base_prompt + _build_section_7(r, unit_name, org_name, ind_name)
        char_count = len(full_prompt)

        cur.execute(
            """
            INSERT INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype,
                mission, system_prompt, character_count, capabilities_json,
                mental_models_json, domain_heuristics_json, technical_vocabulary_json,
                anti_patterns_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                org_unit_id = excluded.org_unit_id,
                name = excluded.name,
                seniority_level = excluded.seniority_level,
                role_archetype = excluded.role_archetype,
                mission = excluded.mission,
                system_prompt = excluded.system_prompt,
                character_count = excluded.character_count,
                capabilities_json = excluded.capabilities_json,
                mental_models_json = excluded.mental_models_json,
                domain_heuristics_json = excluded.domain_heuristics_json,
                technical_vocabulary_json = excluded.technical_vocabulary_json,
                anti_patterns_json = excluded.anti_patterns_json,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (
                role_id, r["org_unit_id"], slug, r["name"], r["seniority_level"], r["role_archetype"],
                r["mission"], full_prompt, char_count, json.dumps(r["capabilities"]),
                json.dumps(r["mental_models"]), json.dumps(r["heuristics"]),
                json.dumps(r["vocabulary"]), json.dumps(r["anti_patterns"]),
                json.dumps({"phase": 14, "domain": "creator_film_media"}),
            ),
        )

        cur.execute(
            """
            INSERT OR REPLACE INTO role_artifacts (id, role_id, artifact_id, direction, frequency, description, metadata_json)
            VALUES (?, ?, ?, 'PRODUCES', 'WEEKLY', ?, '{}');
            """,
            (f"ra_prod_{slug}", role_id, out_art_id, f"{r['name']} produces {out_art_name}"),
        )

        # 5 Day-to-Day Use Cases (strictly 1 per required cadence, >= 2 outputs)
        for idx, (cadence, suffix, trig) in enumerate(cadence_specs, start=1):
            uc_id = f"ruc_{role_id}_{idx}"
            cur.execute(
                """
                INSERT OR REPLACE INTO role_use_cases (
                    id, role_id, title, cadence, trigger_event, inputs_consumed_json,
                    horizontal_tools_json, vertical_tools_json, cognitive_bottlenecks,
                    output_artifacts_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    uc_id, role_id, f"{r['name']}: {suffix}", cadence, trig,
                    json.dumps([r["input_artifact"], "YouTube Studio CTR/AVD & Retention Curves", "Frame.io / StudioBinder Production Log"]),
                    json.dumps(["tool_word_processor", "tool_spreadsheet_processor", "tool_communication_triage"]),
                    json.dumps(creator_tool_ids[:3]),
                    f"Balancing creative originality against quantitative CTR/AVD retention physics and strict budget/turnaround caps for {r['name']}.",
                    json.dumps([f"{out_art_name}_{cadence}_Deliverable", f"{slug}_{cadence}_Telemetry_Verification_Packet"]),
                    json.dumps({"role_seniority": r["seniority_level"], "industry": ind_id, "phase": 14}),
                ),
            )

        # 11 Dual-Layer Tooling Bindings (6 Horizontal + 4 New Creator/Film + 1 Extra Vertical)
        role_tools = HORIZONTAL_TOOL_IDS + creator_tool_ids + [r["extra_vertical_tool"]]
        for t_idx, tool_id in enumerate(role_tools):
            freq = "PRIMARY_DAILY" if (tool_id in creator_tool_ids or t_idx < 3) else "FREQUENT_WEEKLY"
            prof = "EXPERT" if tool_id in creator_tool_ids or t_idx < 2 else "PROFICIENT"
            cur.execute(
                """
                INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(role_id, tool_id) DO UPDATE SET
                    usage_frequency = excluded.usage_frequency,
                    proficiency_level = excluded.proficiency_level,
                    primary_purpose = excluded.primary_purpose;
                """,
                (f"rt_{role_id}_{tool_id}", role_id, tool_id, freq, prof, f"Core creator/film production execution for {r['name']}", '{"phase": 14}'),
            )

        # 6 Acyclic Personal Subagent Swarms
        sixth_code, sixth_label = r["sixth_subagent"]
        swarm_defs = [
            ("MEETING_GRAPH", f"{r['name']} Braintrust & Dailies Note Graph", {"upstream": [], "downstream": ["CHIEF_OF_STAFF"], "triggers": ["table_read", "rough_cut_review"]}),
            ("CHIEF_OF_STAFF", f"{r['name']} Production Chief of Staff", {"upstream": ["MEETING_GRAPH"], "downstream": [sixth_code, "QUANTITATIVE_MODELER"], "triggers": ["slate_intake", "upload_gate"]}),
            (sixth_code, f"{r['name']} {sixth_label}", {"upstream": ["CHIEF_OF_STAFF"], "downstream": ["DOCUMENT_DRAFTER"], "triggers": ["packaging_audit", "retention_check"]}),
            ("QUANTITATIVE_MODELER", f"{r['name']} CTR/AVD & Budget Modeler", {"upstream": ["CHIEF_OF_STAFF"], "downstream": ["DOCUMENT_DRAFTER", "DECK_PRESENTER"], "triggers": ["telemetry_pull", "hot_cost_calc"]}),
            ("DOCUMENT_DRAFTER", f"{r['name']} Script, Coverage & SOP Drafter", {"upstream": [sixth_code, "QUANTITATIVE_MODELER"], "downstream": ["DECK_PRESENTER"], "triggers": ["av_script_draft", "sop_update"]}),
            ("DECK_PRESENTER", f"{r['name']} Lookbook & Packaging Presenter", {"upstream": ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER"], "downstream": [], "triggers": ["greenlight_deck", "thumbnail_board"]}),
        ]
        for sa_code, sa_name, sa_dag in swarm_defs:
            cur.execute(
                """
                INSERT INTO role_subagent_swarms (
                    id, role_id, subagent_name, subagent_role, system_prompt,
                    tool_mcp_bindings_json, interaction_dag_json, hitl_checkpoint, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(role_id, subagent_role) DO UPDATE SET
                    subagent_name = excluded.subagent_name,
                    system_prompt = excluded.system_prompt,
                    interaction_dag_json = excluded.interaction_dag_json;
                """,
                (
                    f"rss_{role_id}_{sa_code.lower()}", role_id, sa_name, sa_code,
                    f"You are {sa_name} (`{sa_code}`) supporting {r['name']}. Enforce first-principles packaging, retention physics, and budget discipline with zero fabricated metrics.",
                    json.dumps(["mcp://youtube_analytics", "mcp://frameio_dailies", "mcp://studiobinder_schedule", "mcp://workspace_docs"]),
                    json.dumps(sa_dag),
                    f"Mandatory human taste, legal/FTC, and final-cut sign-off by {r['name']} prior to publish.",
                    '{"phase": 14}',
                ),
            )

        # 1 GenAI Build Plan
        cur.execute(
            """
            INSERT INTO role_genai_plans (
                id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
                rag_context_architecture, mcp_integrations_json, hitl_guardrails,
                roi_productivity_impact, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(role_id) DO UPDATE SET
                horizontal_genai_spec_json = excluded.horizontal_genai_spec_json,
                vertical_genai_spec_json = excluded.vertical_genai_spec_json,
                rag_context_architecture = excluded.rag_context_architecture;
            """,
            (
                f"rgp_{role_id}", role_id,
                json.dumps({
                    "word_copilot": f"Dual-column AV script, coverage memo & SOP drafting for {r['name']}",
                    "excel_modeler": "Automated CTR x AVD cohort modeling, stripboard hot-costs & sponsorship ROAS waterfalls",
                    "slide_presenter": "Mobile YouTube feed thumbnail saliency boards, greenlight lookbooks & brand wrap decks",
                    "meeting_dispatcher": "Frame-accurate rough-cut Braintrust & table-read action item extraction",
                }),
                json.dumps({
                    "domain_system": "DaVinci Resolve / Premiere Pro + YouTube Studio Analytics + Frame.io + Movie Magic",
                    "capability": "Transcript-synced rough-cut assembly, second-by-second retention dip attribution, and 9:16 multi-platform waterfalling",
                }),
                "Hybrid BM25 lexical + subword LSA semantic RAG indexing historical high-retention scripts, outlier title/thumbnail winners, guild rules, and post-mortem telemetry.",
                json.dumps(["mcp://youtube_studio_analytics", "mcp://frameio_descript", "mcp://davinci_resolve_markers", "mcp://studiobinder"]),
                f"Explicit human approval by {r['name']} required on all public uploads, Title/Thumbnail A/B launches, guild schedules, and FTC disclosures.",
                "45-65% cycle-time reduction across pre-production research, rough-cut assembly, and short-form waterfalling while lifting Browse CTR and 0-30s hook retention.",
                '{"phase": 14}',
            ),
        )

    # 3. Wire Creator & Film Workflow DAG Edges
    for idx, (src_slug, dst_slug, etype, desc) in enumerate(CREATOR_FILM_WORKFLOW_EDGES, start=1):
        cur.execute(
            """
            INSERT OR REPLACE INTO role_edges (
                id, source_role_id, target_role_id, edge_type, description, protocol, cadence, metadata_json
            ) VALUES (?, ?, ?, ?, ?, 'Production Gate Handoff & Telemetry Sync', 'WEEKLY', '{"phase": 14}');
            """,
            (f"edge_p14_{idx}_{src_slug[:22]}_{etype.lower()}", f"role_{src_slug}", f"role_{dst_slug}", etype, desc),
        )

    # 4. Wire baseline employs_role to Media Fortune 500 enterprises so zero orphan roles exist at any point
    media_cos = [
        row[0] for row in cur.execute(
            "SELECT id FROM fortune500_companies WHERE industry_id = 'ind_creative_media' AND rank <= 500 ORDER BY rank LIMIT 10;"
        ).fetchall()
    ]
    for r in all_roles:
        role_id = f"role_{r['slug']}"
        for comp_id in media_cos:
            cur.execute(
                """
                INSERT OR IGNORE INTO employs_role (id, company_id, role_id, department, priority_tier, metadata_json)
                VALUES (?, ?, ?, 'Content, Studio & Digital Creator Production', 'SPECIALIZED', '{"phase": 14}');
                """,
                (f"emp_{comp_id}_{role_id}", comp_id, role_id),
            )

    conn.commit()
    summary = {
        "tools_seeded": len(CREATOR_FILM_VERTICAL_TOOLS),
        "roles_seeded": len(all_roles),
        "workflow_edges_seeded": len(CREATOR_FILM_WORKFLOW_EDGES),
    }
    if owns_conn:
        conn.close()
    return summary


if __name__ == "__main__":
    res = seed_creator_media()
    print(f"SUCCESS: Phase 14 Creator & Film Media seeded: {res}")
