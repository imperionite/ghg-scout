# ghg-scout-ph

**GHG Scout PH** is an open-source, API-driven, databased-backed and MML-enabled community-based greenhouse gas (GHG) emission web application of the [GHG Data Explorer PH](https://ghgph-55623.firebaseapp.com/) designed to **empower schools and LGUs in the Philippines** to monitor, estimate, and visualize their local GHG emissions. It bridges the gap between national-level reporting systems like the [Philippine Greenhouse Gas Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory) and community-level participation.

This tool is designed to be lightweight, educational, and locally relevant — supporting GHG emissions awareness and its climate change impact and reporting at the grassroots level. Please check the [implementation plan](https://github.com/imperionite/ghg-scout/blob/main/IMPLEMENTATION.md) for details.

---

## Objectives

1. **Enable local estimation** of GHG emissions from energy, transport, and waste data.
2. **Provide an educational platform** for environmental awareness and data literacy.
3. **Simulate a participatory reporting system** that could complement national systems like [NICCDIES](https://niccdies.climate.gov.ph/niccdies) and [PGHGIMRS](https://niccdies.climate.gov.ph/ghg-inventory) and its [software model system](https://drive.google.com/file/d/1S8Nh_YMzM4LizaWZ1gNxCKha9REjosyA/view?usp=sharing).
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

### Report Generation & Visualization

* Sector-wise and total GHG emission outputs (in CO₂e)
* Graphical representation of emission breakdowns
* Exportable summaries (PDF/CSV planned)
* Simulated use cases from barangays and schools

### Frontend Microsite

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



```bash

# GET http://localhost:8000/api/ghg/my-summary-interpret HTTP/1.1

HTTP/1.1 200 OK
date: Sun, 15 Jun 2025 17:09:13 GMT
server: uvicorn
content-length: 1945
content-type: application/json
connection: close

{
  "summary_text": "You are a sustainability expert in the Philippines. A university named Dixon Institute located in Manila, NCR, has reported these annual greenhouse gas emissions: 5438.87 kg from agriculture; 5715.76 kg from energy; 5412.48 kg from transport; 5799.34 kg from waste. Give 3 locally relevant ways this university can reduce its emissions, and 1 practical carbon offset strategy suitable for Philippine communities. List them clearly using bullet points.",
  "ai_interpretation": "1. Locally Relevant Ways for Dixon Institute to Reduce Emissions:\n   - Agriculture:\n     * Implement agro-ecological practices such as organic farming, intercropping, and agroforestry to reduce the use of synthetic fertilizers and pesticides.\n     * Promote the use of renewable energy sources for irrigation and other agricultural processes, such as solar-powered water pumps.\n     * Conduct regular waste management and composting programs to reduce the amount of organic waste that ends up in landfills.\n   - Energy:\n     * Conduct an energy audit to identify energy efficiency measures, such as upgrading to energy-efficient appliances and installing insulation.\n     * Invest in renewable energy sources such as solar panels and wind turbines to generate clean energy on campus.\n     * Implement energy conservation practices such as turning off lights and electronics when not in use.\n   - Transport:\n     * Encourage the use of public transportation, carpooling, and cycling to reduce the number of vehicles on campus.\n     * Implement a telecommuting policy for staff and students to reduce the need for daily commuting.\n     * Invest in electric or hybrid vehicles for campus transportation.\n   - Waste:\n     * Implement a comprehensive waste management system, including recycling, composting, and proper disposal of haz",
  "raw_data": {
    "labels": [
      "agriculture",
      "energy",
      "transport",
      "waste"
    ],
    "data": [
      5438.87,
      5715.76,
      5412.48,
      5799.34
    ]
  }
}

```


