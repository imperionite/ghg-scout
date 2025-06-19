## GHG Scout PH: Project Documentation and Implementation Plan

**Project Title:** GHG Scout PH: A Community-Based GHG Estimation and Awareness Tool<br>
**Project Type:** Proof of Concept (POC)<br>
**Duration:** Less than a month<br>
**Target Users:** Philippine Schools and LGU Units<br>  
**Tools & Technologies:** FastAPI (backend API), MongoDB (database), React (frontend), Streamlit (data visualization), CSV/Mock data<br>

---

## Introduction

**GHG Scout PH** is a prototype API-driven, database-backed, and Large Language Model (LLM)-enabled software application designed to empower local communities—particularly schools and Local Government Units (LGUs)—to estimate and interpret their greenhouse gas (GHG) emissions in a simplified, accessible, and localized manner.

Inspired by the national initiative, the [Philippine Greenhouse Gas Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory) and [its software model](https://drive.google.com/file/d/1S8Nh_YMzM4LizaWZ1gNxCKha9REjosyA/view?usp=sharing) under the [National Integrated Climate Change Database Information and Exchange System (NICCDIES)](https://niccdies.climate.gov.ph/niccdies) and the [IPCC guidelines](https://www.ipcc-nggip.iges.or.jp/public/2006gl/), this project aims to raise awareness and simulate community-level implementation of GHG monitoring, ensuring scientific rigor, local relevance, and universal applicability.

Community-level GHG monitoring is vital for fostering local climate action, enhancing data granularity, and supporting national climate commitments.

---

## Scientific and Methodological Foundations

- **Emission factors and formulas** are based on the [Philippine GHG Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory), the Philippine GHG Manual, and the [IPCC 2006 Guidelines for National Greenhouse Gas Inventories](https://www.ipcc-nggip.iges.or.jp/public/2006gl/).
- **Sector coverage** aligns with national and international standards:  
  - Energy  
  - Transport  
  - Waste  
  - Agriculture  
  - Industrial Processes and Product Use (IPPU)
- **Data collection** is simplified for community use but captures all major emission drivers for scientifically sound estimation and reporting.
- **SMEs** can use this application if they are interested in basic GHG accounting, but the current model is best for community-scale tracking, not detailed business inventories (which often require more granular data: energy by process, refrigerants, product use, etc.).

---

## Project Objectives

- Simulate localized GHG estimation using real-world parameters at the school and LGU level.
- Develop an interactive, educational tool that supports local climate change awareness and engagement.
- Visualize emission trends by sector: energy, transport, and waste.
- Showcase how community-level tools can complement national inventory systems like PGHGIMRS.
- Facilitate user feedback collection to improve tool effectiveness and usability.
- Provide AI-driven, personalized recommendations for reducing emissions and adopting carbon offset strategies, tailored to each community’s data and context.

---

## Core Features

### GHG Estimator Tool

- Input categories:
  - Electricity and fuel consumption
  - Local transport usage (e.g., jeepneys, tricycles)
  - Waste volume and management practices
- Emission factors pre-loaded based on Philippine standards or IPCC defaults.
- Outputs estimated GHG emissions in CO2e (tonnes/year or kg/month).
- Clear display of emission breakdown by sector.

### Mock Dashboard (Simulation)

- Pre-filled data for 2-3+ LGU/school examples with diverse profiles.
- Sector-wise GHG output visualized via bar charts, pie charts, and trend lines.
- Downloadable reports in PDF and CSV formats.

### Public Awareness Microsite

- Basic information on PGHGIMRS and NICCDIES.
- Educational pages such as "Why measure emissions?" and "Your community's climate impact".
- Frequently Asked Questions (FAQ) and resource links.
- Optional interactive map showing participating barangays/schools.

### Optional Add-ons (If Time Permits)

- User feedback form for continuous improvement.
- Simple leaderboard or recognition badges (Gold/Silver/Green Scout) to motivate participation.

---

## Technical Architecture

| Component          | Stack/Tool                          | Notes                                        |
| ------------------ | ----------------------------------- | -------------------------------------------- |
| Backend API        | FastAPI                             | RESTful API handling authentication and data |
| Database           | MongoDB                             | Stores user and GHG data                     |
| Frontend Microsite | React                               | Static site consuming FastAPI endpoints      |
| Data Visualization | Chart.js/Streamlit                  | Dashboard for interactive data exploration   |
| Data Storage (POC) | MongoDB + Mock data                 | Initial data for simulation                  |
| Deployment         | Streamlit Cloud, Render.com, Vercel | Backend and frontend deployed separately     |

---

## Implementation Timeline (20-Day Sprint)

| Day   | Task                                                                |
| ----- | ------------------------------------------------------------------- |
| 1-2   | Finalize scope, emission factors, data schema                       |
| 3-5   | Develop FastAPI backend and MongoDB models                          |
| 6-8   | Build GHG estimation logic + Streamlit data visualization dashboard |
| 9-10  | Add CSV/PDF export feature                                          |
| 11-12 | Build frontend using AstroJS                                        |
| 13-15 | Simulate sample LGU/school data use cases                           |
| 16-17 | Final UI polish, accessibility improvements, testing                |
| 18    | Write documentation, glossary, and prepare poster/demo              |
| 19    | Conduct dry-run presentation and gather feedback                    |
| 20    | Submission and deployment                                           |

---

## Alignment with National Framework

This project draws direct inspiration from [PGHGIMRS](https://niccdies.climate.gov.ph/ghg-inventory) and [NICCDIES](https://niccdies.climate.gov.ph/niccdies), designed to:

- Complement national systems with grassroots data awareness.
- Encourage civic participation in climate monitoring and reporting.
- Provide a low-barrier pathway for LGUs and schools to engage in climate action.
- Ensure data privacy and security by managing user authentication and access control.

---

## Deliverables

- Working API-based web app (FastAPI + MongoDB backend).
- Public-facing microsite (React).
- Chart.js/Streamlit-based data visualization dashboard.
- Sample use cases with mock data.
- Technical documentation including API specs, user guide, and glossary.
- Visual project report/poster for dissemination.

---

## Data Submission Model

All sector models are **optional-entry** and default to zero, so users can submit only what’s relevant to them. This supports broad participation and data aggregation without forcing full completion.

### Example: Energy Sector Model

```python
class GHGSubmissionEnergy(BaseModel):
    sector: Literal["energy"] = "energy"
    electricity_consumed_kwh: Optional[float] = 0.0
    lpg_used_kg: Optional[float] = 0.0
    kerosene_used_liters: Optional[float] = 0.0
    firewood_used_kg: Optional[float] = 0.0
    diesel_used_liters: Optional[float] = 0.0
    gasoline_used_liters: Optional[float] = 0.0
    coal_used_kg: Optional[float] = 0.0
```

*(See full models in the codebase for Transport, Waste, Agriculture, and IPPU.)*

---

## Emission Factors

Emission factors are based on Philippine and IPCC standards, and are transparently documented:

| Activity/Fuel            | Unit      | Emission Factor (kg CO2e/unit) | Source         |
|--------------------------|-----------|-------------------------------|----------------|
| Electricity (grid)       | kWh       | 0.709                         | PGHGIMRS/IPCC  |
| LPG                      | kg        | 2.983                         | PGHGIMRS/IPCC  |
| Kerosene                 | liter     | 2.391                         | PGHGIMRS/IPCC  |
| Firewood                 | kg        | 0.015                         | PGHGIMRS/IPCC  |
| Diesel                   | liter     | 2.68                          | PGHGIMRS/IPCC  |
| Gasoline                 | liter     | 2.32                          | PGHGIMRS/IPCC  |
| Coal                     | kg        | 2.42                          | PGHGIMRS/IPCC  |
| Cattle                   | head/year | 912.5                         | PGHGIMRS/IPCC  |
| Carabao                  | head/year | 730                           | PGHGIMRS/IPCC  |
| Goat                     | head/year | 182.5                         | PGHGIMRS/IPCC  |
| Pig                      | head/year | 401.5                         | PGHGIMRS/IPCC  |
| Chicken                  | head/year | 7.3                           | PGHGIMRS/IPCC  |
| Fertilizer (N)           | kg        | 5.5                           | PGHGIMRS/IPCC  |
| Rice (continuous)        | ha/year   | 1200                          | PGHGIMRS/IPCC  |
| Rice (intermittent)      | ha/year   | 800                           | PGHGIMRS/IPCC  |
| Rice (dry)               | ha/year   | 100                           | PGHGIMRS/IPCC  |
| Landfill Waste           | kg        | 1.8                           | PGHGIMRS/IPCC  |
| Composting Waste         | kg        | 0.2                           | PGHGIMRS/IPCC  |
| Incineration Waste       | kg        | 2.0                           | PGHGIMRS/IPCC  |
| Cement                   | tonne     | 800                           | PGHGIMRS/IPCC  |
| Lime                     | tonne     | 900                           | PGHGIMRS/IPCC  |
| Steel                    | tonne     | 1800                          | PGHGIMRS/IPCC  |
| Refrigerant (HFC-134a)   | kg        | 1430                          | PGHGIMRS/IPCC  |
| Solvent                  | liter     | 2.0                           | PGHGIMRS/IPCC  |
| Other Process Emissions  | tonne     | 1000                          | PGHGIMRS/IPCC  |

*Emission factors are periodically reviewed and updated as new national data becomes available.*

---

## Calculation Formulas

Each sector uses a transparent, reference-based calculation.  
**Example: Energy Sector**

```python
co2e = (
    electricity_consumed_kwh * 0.709 +
    lpg_used_kg * 2.983 +
    kerosene_used_liters * 2.391 +
    firewood_used_kg * 0.015 +
    diesel_used_liters * 2.68 +
    gasoline_used_liters * 2.32 +
    coal_used_kg * 2.42
)
```

**Other sectors** (Transport, Waste, Agriculture, IPPU) use analogous formulas, multiplying user input by scientifically established emission factors.
---

## Principles and Best Practices

- **Simplicity & Accessibility:**  
  All fields are optional or default to zero. Users are never forced to fill every field, enabling broad participation and partial inventories.

- **Scientific Rigor:**  
  All calculations are traceable to Philippine national methodologies and IPCC guidelines.

- **Transparency:**  
  Emission factors and formulas are openly documented and referenced.

- **Extensibility:**  
  The system is designed for iterative improvement: emission factors, models, and logic can be updated as better data or peer-reviewed methods become available.

---

## References

- [Philippine GHG Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory)
- [Philippine GHG Manual](https://niccdies.climate.gov.ph/sites/default/files/2021-09/Philippine%20GHG%20Manual%20Volume%201.pdf)
- [IPCC 2006 Guidelines for National Greenhouse Gas Inventories](https://www.ipcc-nggip.iges.or.jp/public/2006gl/)

---

## Attribution

GHG Scout PH is inspired by the Philippine Climate Change Commission’s national GHG inventory and is designed for community-level empowerment, transparency, and scientific integrity.

---

## Future Possibilities

- Integration with real GHG data sources and official NICCDIES pipelines.
- Localization and incorporation of local dialects for accessibility.
- Real-time data submission by partner schools and LGUs.
- Partnerships with local government units and NGOs for data validation and outreach.
- Enhanced user engagement features such as gamification and community forums.

---

**Prepared by:** Arnel Imperial<br>
**Course:** People and Earth’s Ecosystem (PEE)<br> 
**Institution:** MMDC<br> 
**Date:** 06.14.2025<br>
