# ghg-scout-ph

**GHG Scout PH** is an open-source, API-driven, community-based greenhouse gas (GHG) emission web application of the [GHG Data Explorer PH](https://ghgph-55623.firebaseapp.com/) designed to **empower schools and LGUs in the Philippines** to monitor, estimate, and visualize their local GHG emissions. It bridges the gap between national-level reporting systems like the [Philippine Greenhouse Gas Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory) and community-level participation.

This tool is designed to be lightweight, educational, and locally relevant — supporting GHG emissions awareness and its climate change impact and reporting at the grassroots level. Please check the [implementation plan](https://github.com/imperionite/ghg-scout/blob/main/IMPLEMENTATION.md) for details.

---

## Objectives

1. **Enable local estimation** of GHG emissions from energy, transport, and waste data.
2. **Provide an educational platform** for environmental awareness and data literacy.
3. **Simulate a participatory reporting system** that could complement national systems like [NICCDIES](https://niccdies.climate.gov.ph/niccdies) and [PGHGIMRS](https://niccdies.climate.gov.ph/ghg-inventory) and its [software model system](https://drive.google.com/file/d/1S8Nh_YMzM4LizaWZ1gNxCKha9REjosyA/view?usp=sharing) .
4. **Demonstrate secure and ethical data practices** in building digital tools for the public.

---

## Key Features

### User Authentication 

* Secure user registration with **username, password, and community affiliation** (LGU or School)
* Token-based login and authorization system (non-JWT)
* Secure storage of user credentials with **SHA-256 hashing**
* Built-in token validation for protected endpoints

### GHG Estimation & Data Collection

* Users can enter local data related to:

  * Household/school **electricity and fuel consumption**
  * Community/school **transport usage**
  * Daily or monthly **waste volume**
* Emission factors are based on IPCC guidelines, with potential for localization

### Report Generation & Visualization (Streamlit)

* Sector-wise and total GHG emission outputs (in CO₂e)
* Graphical representation of emission breakdowns
* Exportable summaries (PDF/CSV planned)
* Simulated use cases from barangays and schools

### Frontend Microsite (AstroJS)

* Educational content:

  * What are GHGs?
  * Why measure emissions?
  * How this project connects to PH initiatives
* Map of participating communities (future enhancement)
* Public-facing dashboard for showcasing results

---

## Architecture

| Component          | Technology                   |
| ------------------ | ---------------------------- |
| Backend API        | FastAPI (Python)             |
| Database           | MongoDB (via Docker)         |
| Frontend Microsite | AstroJS                      |
| Data Visualization | Streamlit                    |
| Auth System        | Basic token authentication   |
| Deployment         | Local or Render.com / Vercel |

---

## Sample Use Case (Simulation)

> **Barangay San Juan** enters their average monthly electricity bill, jeepney count, and daily waste volume. The system estimates \~5.4 tonnes CO₂e/month. Most emissions come from waste methane. A visual report is generated, showing the breakdown and potential areas for reduction.

---

## Compliance and Ethics

This system is designed in accordance with the **Philippine Data Privacy Act of 2012 (RA 10173)**:

* No sensitive personal data is collected
* Passwords are securely hashed
* User data is limited to what's essential (username, affiliation)
* Usage is transparent and educational

## CLI Commands

Please check this [link](https://github.com/imperionite/ghg-scout/blob/main/RUNNING.md).

## Implementation Plan

Please check this [link](https://github.com/imperionite/ghg-scout/blob/main/IMPLEMENTATION.md).


