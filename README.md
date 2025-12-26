# Infrastructure Inequality Dashboard  
### Quantifying Essential Construction Reliance Across Los Angeles Neighborhoods

This project builds an interactive analytics dashboard to uncover how income inequality shapes construction and infrastructure priorities across Los Angeles. By combining building permit records with census-based income classifications, the dashboard quantifies essential vs. discretionary construction patterns and visualizes structural disparities across neighborhoods.

---

##  Problem
Urban policy teams lack a clear, data-driven way to understand whether construction activity in low-income neighborhoods represents **growth** or **basic survival-level maintenance**.  
Although Los Angeles publishes detailed permit data, it is fragmented, large-scale, and not directly usable for policy decision-making.

---

##  Outcome (Measurable)
This dashboard improves visibility into infrastructure inequality by quantifying the **essential construction reliance gap (%)** between income groups.

**Key Finding:**  
- Low-income neighborhoods rely on essential construction for **~65.9%** of permits  
- High-income neighborhoods rely on **~52.1%**  
➡️ **A ~13.8 percentage point disparity**

This metric provides a concrete signal for policymakers to prioritize equitable infrastructure investment.

---

##  Domain Insight
Not all permits represent equal value.  
Some indicate *improvement* (renovations, additions), while others indicate *survival* (safety repairs, utilities, stabilization).

This project reframes construction analysis into:
- **Essential Permits** → safety, utilities, critical repairs  
- **Non-Essential Permits** → upgrades, additions, discretionary improvements  

A lens commonly overlooked in purely technical analyses.

---

##  Tech Stack
| Tool | Purpose |
|------|---------|
| **Snowflake (Snowpark)** | Scalable querying & joining of large permit + census datasets |
| **Python (Pandas)** | Data cleaning, transformation, classification logic |
| **Streamlit** | Interactive dashboard UI |
| **Plotly** | Comparative & cumulative visualizations |
| **Jupyter / VS Code** | Exploration & prototyping |

---

##  Features
- Classifies permits into **Essential** vs. **Non-Essential**
- Compares construction reliance across **income-based neighborhood groups**
- Displays interactive charts:  
  - Permit composition  
  - Essential reliance deltas  
  - Neighborhood-level cumulative patterns  
  - Category-level comparison  
- Supports dynamic filtering for policy exploration
- Exports insights for briefing or policymaker review

---

## Example Visuals (Add Screenshots Later)
