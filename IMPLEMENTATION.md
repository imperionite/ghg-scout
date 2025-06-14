# ghg-scout: Project Documentation and Implementation Plan

**Project Title:** GHG Scout PH: A Community-Based GHG Estimation and Awareness Tool<br>
**Project Type:** Proof of Concept (POC)<br>
**Duration:** Less than a month<br>
**Target Users:** Philippine Schools and LGU Units<br>
**Tools & Technologies:** FastAPI (backend API), MongoDB (database), AstroJS (frontend), Streamlit (data visualization), CSV/Mock data

---

## Introduction

**GHG Scout PH** is a prototype API-based and database-driven web application that empowers local communities—particularly schools and LGUs—to estimate their greenhouse gas (GHG) emissions in a simplified, accessible, and localized manner.

Inspired by the existing national initiative, the [Philippine Greenhouse Gas Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory) and [its software model system](https://drive.google.com/file/d/1S8Nh_YMzM4LizaWZ1gNxCKha9REjosyA/view?usp=sharing), under the [National Integrated Climate Change Database Information and Exchange System (NICCDIES)](https://niccdies.climate.gov.ph/niccdies), this project aims to create awareness and simulate how such a system could be implemented at the community level.

---

## Project Objectives

1. To simulate localized GHG estimation using real-world parameters at the school and LGU level
2. To develop an interactive and educational tool that supports local climate change awareness
3. To visualize emission trends by sector: energy, transport, and waste
4. To showcase how community-level tools can support national inventory systems like PGHGIMRS

---

## Core Features

### **GHG Estimator Tool**

* Input categories:

  * Electricity and fuel consumption
  * Local transport usage
  * Waste volume and management
* Emission factors pre-loaded based on PH standards or IPCC defaults
* Estimated output in CO2e (tonnes/year or kg/month)

### **Mock Dashboard (for simulation only)**

* Pre-filled data for 2-3 or more (if time permits) LGU/school examples
* Sector-wise GHG output and total footprint
* Downloadable reports (PDF/CSV)

### **Public Awareness Microsite**

* Basic content on PGHGIMRS and NICCDIES
* Educational pages ("Why measure emissions?", "Your community's climate impact")
* Optional: Participating barangays/schools map

### **Optional Add-ons (if time permits)**

* Feedback form
* Simple leaderboard or recognition badges (Gold/Silver/Green Scout)

---

## Technical Architecture

| Component          | Stack/Tool                             |
| ------------------ | -------------------------------------- |
| Backend API        | FastAPI                                |
| Database           | MongoDB                                |
| Frontend Microsite | AstroJS                                |
| Data Visualization | Streamlit                              |
| Data Storage (POC) | MongoDB + Mock data                    |
| Deployment         | Streamlit Cloud, Render.com, or Vercel |

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
| 16-17 | Final UI polish, testing                                            |
| 18    | Write documentation and prepare poster/demo                         |
| 19    | Conduct dry-run presentation (if applicable)                        |
| 20    | Submission and deployment                                           |

---

## Sample Use Case (Simulated)

* **Barangay San Juan**: Inputs monthly waste volume, number of jeepneys and tricycles, and energy bills
* **Output**: 5.4 tonnes CO2e/month, with largest share from waste methane emissions
* **Report**: Downloadable summary with charts and community recommendations

---

## Alignment with National Framework

This project draws direct inspiration from [PGHGIMRS](https://niccdies.climate.gov.ph/ghg-inventory) and [its software](https://drive.google.com/file/d/1S8Nh_YMzM4LizaWZ1gNxCKha9REjosyA/view?usp=sharing) and [NICCDIES](https://niccdies.climate.gov.ph/niccdies). Although it is a prototype, it is designed to:

* Complement national systems with grassroots data awareness
* Encourage civic participation in climate monitoring
* Provide a low-barrier pathway for LGUs and schools to engage in climate reporting

---

## Deliverables

* Working API-based web app (FastAPI + MongoDB backend)
* Public-facing microsite (AstroJS)
* Streamlit-based data visualization dashboard
* Sample use cases with mock data
* Technical documentation and visual project report/poster

---

## Future Possibilities

* Integration with real GHG data sources
* Incorporation of local dialects for accessibility
* Real-time data submission by partner schools/LGUs
* Connection with official NICCDIES data pipelines (long-term)

---

**Prepared by:** Arnel Imperial<br>
**Course:** People and Earth’s Ecosystem (PEE)<br>
**Institution:** MMDC<br>
**Date:** 06.14.2025
