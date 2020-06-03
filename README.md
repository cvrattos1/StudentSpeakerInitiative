# Students' Speaker Initiative Web Application
This project is a three-tier web application that serves as a voting platform for the new student group known as the Students' Speaker Initiative (SSI). Each semester, the SSI intends to run two concurrent, but distinct election cycles. The first election cycle is for the selection of an individual speaker to bring to campus; the second election cycle is for the selection of a panel of speakers. Both cycles are divided into four successive phases. The four phases are the following: _nominations_, _endorsements_, _voting_, and _results_.

## For Students
- The first phase is the nomination phase. During this phase, students will be able to log into the application and nominate a set number of speakers and/or panels. Specifically for panels, any panel that has been nominated must first be approved by a faculty member before it can move into the next phases of the cycle.
- The second phase is the endorsement phase. During this phase, students may endorse a set number of speakers and/or panels. Any given speaker or panel can only be endorsed once per student. Endorsements serve to gauge initial interest, which is why only speakers/panels that receive a minimum number of endorsements can move into the next phase of the cycle. Students may flag any speaker(s) for additional review by admins if that speaker appears to be spam or a fraudulent nomination.
- The third phase is the voting phase. During this phase, students may vote for speakers and/or panels. Students are given a set number of allotted votes and may distribute them however they see fit. 
- The fourth and final phase is the results phase. During this phase, the students may view the final standings of the speakers and panels after the vote. The speaker and panel with the most votes will have won, and the SSI will then work to bring that speaker and panel to campus.

## For Admins
- Admins are responsible for creating new election cycles and establishing each cycle's parameters. This includes setting up the cycle's start/end dates and determining how many nominations, endorsements, and votes students can use during a cycle. 
- Admins also have the ability to add new admins, delete old admins, and review flagged speakers. When reviewing reports, admins have the option to either dismiss a report (in which case the flagged speaker remains in the cycle) or approve the report (in which case the flagged speaker is removed from the cycle).
- All actions taken by admins are recorded in the admin logs, which are shown to both students and admins.

## For Faculty
- Per the SSI's request, faculty may log into the application and approve a panel of speakers during the nomination phase of a cycle. This allows faculty to get involved with the election cycle and provides a kind of vetting system for the nominated panels.
- Faculty may also log into the system during the results phase of the cycle to view the final standings of the panels and see which panel has won the vote.
