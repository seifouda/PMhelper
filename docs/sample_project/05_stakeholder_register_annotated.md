# Stakeholder Register — Annotated Educational Version

## PMHelper_Edu Development Project

> **How to use this document:**
> Annotated companion to `05_stakeholder_register.md`. Teaching notes explain the
> _methodology_ behind each stakeholder analysis decision.

---

| Field               | Value                                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| **Document ID**     | PMHE-2025-SR-001-EDU                                                                                 |
| **Companion to**    | PMHE-2025-SR-001 (Professional)                                                                      |
| **PMBOK Alignment** | Initiating: Process 13.1 (Identify Stakeholders); Planning/Executing/Monitoring: Processes 13.2–13.4 |
| **Knowledge Area**  | Stakeholder Management                                                                               |

---

## What Is Stakeholder Management? Why Is It a Separate Knowledge Area?

> **📚 Core Concept**
>
> PMBOK 6th Edition elevated Stakeholder Management to a full Knowledge Area (Area 13)
> with four dedicated processes. This elevation reflects decades of project failure
> analysis that consistently found stakeholder misalignment — not technical problems —
> as the leading cause of project failures.
>
> The four processes:
>
> - **13.1 Identify Stakeholders** — Who is affected? Who can affect us? (This document)
> - **13.2 Plan Stakeholder Engagement** — What is our strategy for each?
> - **13.3 Manage Stakeholder Engagement** — Execute the strategy
> - **13.4 Monitor Stakeholder Engagement** — Is the strategy working?
>
> **PMP exam focus:** Process 13.1 is in the _Initiating_ group and runs throughout the
> project. New stakeholders are discovered continuously. A PM who identifies all
> stakeholders at the start and never revisits the list is failing Process 13.4.

---

## Section 2 — Why 20 Stakeholders for a Small Project?

> **📚 Teaching Note — The Hidden Stakeholders**
>
> Students often limit their stakeholder list to the obvious people: sponsor, PM, team.
> The professional register here identifies 20 stakeholders. The "hidden" ones are
> educationally important:
>
> **SR-013 (University IT Departments):** These are often the stakeholders who
> _kill projects_ at the last moment. A faculty member adopts the tool, students
> are excited — then IT says "we cannot install unsigned executables on lab computers."
> The project anticipated this with the `--onedir` build and AV-safe manifest (see
> repository file `pmhelper_edu.manifest`). This stakeholder directly influenced
> a technical requirement.
>
> **SR-016 (Competing Software Providers):** Competitors are stakeholders? Yes — they
> affect the project's environment even if they don't participate. Monitoring their
> moves is part of risk management. If Microsoft offers free educational Project licenses,
> the entire business case changes.
>
> **SR-020 (Future Employers of Students):** The ultimate test of an educational tool
> is whether graduates are better prepared for industry. This stakeholder never interacts
> with the project but defines the standard the product must meet.
>
> **Identification methods (PMBOK Process 13.1 tools):**
>
> - Stakeholder analysis (who benefits? who is affected?)
> - Expert judgment (Prof. Youssef's perspective on the academic community)
> - Meetings and brainstorming (project team kickoff)
> - Data representation (power/interest grid, Section 5)

---

## Section 3 — Deep Dives on Key Stakeholder Entries

### SR-003 (Lead Developer) — The "Single Point of Failure" Stakeholder

> **📚 Why the Lead Developer Is a Critical Stakeholder, Not Just a Team Member**
>
> Students are sometimes surprised to see team members in a stakeholder register.
> In PMBOK terms, _anyone_ who can affect or be affected by the project is a
> stakeholder — including the project team.
>
> Omar Hassan El-Rashidy holds a unique position: he is simultaneously:
>
> - The person delivering the primary output
> - The holder of all technical knowledge
> - A stakeholder with personal interests (technical quality, work-life balance)
> - A single point of failure (Risk R-001)
>
> The special note "protect from direct stakeholder pressure" is a management action.
> If faculty partners or the sponsor contact Omar directly with feature requests,
> he faces conflicting priorities. The PM creates a buffer to prevent this from
> affecting delivery.
>
> **Lesson:** Managing your own team members as stakeholders — understanding their
> interests, concerns, and engagement levels — is one of the most overlooked PM skills.

### SR-007 (University Faculty) — The Adoption Gate

> **📚 Teaching Note — High Influence Without High Power**
>
> Faculty have "Low" direct power over project decisions but "High" influence on
> adoption outcomes. This is a distinction PMBOK makes but students often conflate.
>
> Faculty can't change what the project delivers. But they decide whether the product
> is used. Their influence is expressed _after_ the project ends, during benefits
> realisation.
>
> The engagement gap strategy is: Unaware → Supportive.
>
> **How do you move a stakeholder from Unaware to Supportive?**
>
> 1. Awareness campaign (announcement at release)
> 2. Beta testing with 2–3 trusted faculty partners (making them co-creators)
> 3. Documentation that makes adoption effortless
> 4. The reference sample project (this document set) as ready-made course material
>
> **Notice that the reference sample project you are reading is itself a stakeholder
> management tool** — it reduces the effort required for faculty adoption.

### SR-012 (Department Administration) — Keep Satisfied, Not Ignore

> **📚 Teaching Note — The "Keep Satisfied" Trap**
>
> Stakeholders in the "Keep Satisfied" quadrant (High Power, Low Interest) are often
> the most dangerous if ignored. They don't care about day-to-day project details,
> but if they become concerned — about security, cost, liability, or reputation —
> they can block everything immediately.
>
> The strategy "Neutral to Supportive by Q4 2026" requires specific actions:
>
> - An institutional adoption package (not a generic marketing brochure)
> - A security summary document (addressing IT concerns proactively)
> - A reference letter from Prof. Youssef's institution (social proof)
>
> **Real-world trap:** PMs who are laser-focused on delivery sometimes forget to keep
> institutional gatekeepers informed. The product launches; faculty love it; students
> want to use it. Then the Dean's office asks "what is this tool? Did we approve it?"
> A proactive communication plan prevents this scenario.

---

## Section 4 — Stakeholder Engagement Assessment Matrix

> **📚 Teaching Note — The 5-Level Engagement Scale**
>
> The five engagement levels (Unaware → Resistant → Neutral → Supportive → Leading)
> are from PMBOK Process 13.2 (Plan Stakeholder Engagement).
>
> The matrix shows two things per stakeholder:
>
> - **Current level** (where they are at the assessment date)
> - **Desired level** (where the PM wants them to be)
>
> The **gap** between current and desired is the management task.
>
> **Important: Not all stakeholders need to be "Leading"**
>
> Look at SR-016 (Competitors) — the desired level is "Unaware." The strategy is to
> remain invisible to competitors during development. This is unusual but intentional.
> For a first-mover open-source product, stealth during development maximises the
> advantage at launch.
>
> And SR-013 (IT Departments) — desired level is "Neutral." They don't need to be
> enthusiastic about the product; they just need to not block it. Designing the product
> to meet their technical requirements (no admin rights, AV-safe) achieves Neutral
> without requiring any relationship management.
>
> **This demonstrates a key principle:** Different stakeholders require different
> engagement strategies. A one-size-fits-all communication plan is almost always wrong.

---

## Section 5 — Power / Interest Grid

> **📚 Teaching Note — Using the Grid for Planning**
>
> The Power/Interest grid (also called the "Stakeholder Matrix") is a visual tool
> for prioritising stakeholder management effort. The four quadrants prescribe:
>
> | Quadrant                  | Strategy       | Why                                        |
> | ------------------------- | -------------- | ------------------------------------------ |
> | High Power, High Interest | Manage Closely | They care deeply AND can change outcomes   |
> | High Power, Low Interest  | Keep Satisfied | They can block the project if displeased   |
> | Low Power, High Interest  | Keep Informed  | They care but can't change decisions       |
> | Low Power, Low Interest   | Monitor        | Low investment required; watch for changes |
>
> **Notice the asymmetry:** High Power stakeholders with Low Interest are MORE
> dangerous than Low Power stakeholders with High Interest. A student who dislikes
> the product can't kill it. A Dean who is ignored might.
>
> **Practice question:** SR-016 (Competing Vendors) are placed in the Bottom-Left
> quadrant (Low Power, Low Interest from the project's perspective). However, the
> text says they have "High" power over adoption outcomes. Why the discrepancy?
>
> _Answer: Their power is over the MARKET, not over the PROJECT. Power in the grid
> refers to ability to influence the project execution — not the business outcome.
> This distinction matters for understanding what the grid actually measures._

---

## Section 6 — Communication Approach

> **📚 Teaching Note — Managing in Four Directions**
>
> Effective stakeholder communication requires managing in four directions:
>
> **Managing UP** (Sponsor, SR-001): Formal, structured, evidence-based.
> The sponsor wants to know: "Are we on track? Are there issues I need to decide?"
> Weekly financial status + monthly formal report serves this need.
>
> **Managing DOWN** (Team members, SR-003–005): Supportive, collaborative, enabling.
> The team needs: "What do I do next? Is my work on track? Am I supported?"
> Daily standup + sprint reviews serve this need.
>
> **Managing ACROSS** (Technical Advisor, SR-006): Collegial, content-focused.
> Prof. Youssef needs: "Is the content educationally correct?"
> Monthly content reviews serve this need.
>
> **Managing OUT** (All external stakeholders, SR-007–020): Strategic, purposeful.
> External stakeholders receive information appropriate to their interest level —
> not the same depth as the internal team.
>
> **Key principle:** The PM communicates differently to each group. A status report
> for the sponsor looks nothing like a sprint standup message to the developer.
> Using the wrong format for the wrong audience is a communication failure even if
> the information is correct.

---

## Notable Stakeholder Management Decisions in This Project

> **📚 Three Management Choices Worth Discussing**
>
> **1. Beta Testing with Faculty Partners (SR-007)**
>
> Engaging 2–3 faculty members as beta testers before launch is a stakeholder
> management technique called **co-creation**. By involving them early:
>
> - They become advocates, not just users
> - Their feedback improves the product before general release
> - Their institutional credibility transfers to the product
>
> **2. Documentation as Stakeholder Management (SR-013)**
>
> The IT Department stakeholder is "managed" entirely through documentation —
> system requirements doc, AV-safe manifest explanation, no admin rights requirement.
> This is efficient: instead of building 50 individual relationships with IT teams,
> one well-written technical document achieves Neutral engagement across all of them.
>
> **3. The "Desired = Unaware" Strategy (SR-016)**
>
> Deliberately keeping competitors unaware during development is an unconventional
> but defensible strategy. Open-source projects that announce early often attract
> competing forks before they have established a user community. First-mover adoption
> is a stronger defence than patents or secrecy in open-source markets.

---

## 📋 Review Questions (Self-Assessment)

1. SR-013 (University IT Departments) has "Medium-High" power but "Unaware"
   current engagement. If they discover the project through a faculty beta test and
   raise a security concern, what engagement level have they suddenly reached?
   What would the PM's immediate response be?

2. The engagement matrix shows SR-007 (Faculty) at "Unaware" current engagement.
   The document revision history (version 1.1) notes they have moved to "Neutral."
   What specific event caused this change, and how should the PM document it?

3. The Power/Interest grid places SR-016 (Competitors) in the bottom-left quadrant
   (Monitor). Yet the risk register includes no risk related to competitive response.
   Should it? Write a risk entry for competitive response using the standard risk
   format (ID, description, probability, impact, response).

4. Compare the communication approach for SR-001 (Sponsor) versus SR-009 (UG Students).
   Both are "High Interest" stakeholders. Why are their communication strategies so
   different? What does this reveal about the relationship between interest and
   communication frequency?

5. SR-020 (Future Employers) has desired engagement of "Neutral" — meaning the
   PM does not want them to be aware of the project at all. Yet they are listed as
   stakeholders. Explain the reasoning: why identify a stakeholder whose desired
   state is to remain unaware?

6. You are the PM. The project is in Phase 5. A new stakeholder appears: a PhD
   student at a regional university who has found the GitHub repository, filed 3
   detailed bug reports, and is asking about contributing code. Which quadrant do
   they belong in? What is their engagement level? What would you do?

---

_Document ends. Proceed to:_ [06_requirements_traceability_matrix.md](06_requirements_traceability_matrix.md)
