from typing import List, Dict, Any, Tuple
from pydantic import BaseModel
from collections import defaultdict
from app.services.interactions.interaction_engine import InteractionRecord, SeverityLevel

class MedicationDosage(BaseModel):
    """Data Transfer Object representing a medication to be scheduled and its required frequency."""
    drug_name: str
    frequency: int  # Doses per day (e.g., 2 = twice daily)

class ScheduleOptimizer:
    """
    Intelligent medication scheduling engine.
    
    Generates an optimized daily timeline minimizing pharmacodynamic overlap
    by separating conflicting medications based on severity constraints.
    Operates strictly deterministically in O(M*S*M) complexity.
    """
    
    # 8 discrete 2-hour slots representing a typical 16-hour waking day
    # (08:00 to 22:00)
    AVAILABLE_SLOTS = [8, 10, 12, 14, 16, 18, 20, 22]
    
    # Required temporal separation (in hours) based on interaction severity
    SEPARATION_CONSTRAINTS = {
        SeverityLevel.SEVERE: 4,
        SeverityLevel.MODERATE: 2,
        SeverityLevel.MILD: 0, # Allowed to be taken together if necessary, but ideally separated
        SeverityLevel.CONTRAINDICATED: 24 # Cannot be scheduled on the same day safely
    }

    def _build_constraint_graph(self, interactions: List[InteractionRecord]) -> Dict[str, Dict[str, int]]:
        """
        Maps DrugA -> DrugB -> Minimum Required Separation Hours.
        """
        constraint_map = defaultdict(dict)
        for interaction in interactions:
            drug_a = interaction.drug_a.upper()
            drug_b = interaction.drug_b.upper()
            required_gap = self.SEPARATION_CONSTRAINTS[interaction.severity]
            
            # Keep the strictest (longest) required separation if multiple rules exist
            if drug_b not in constraint_map[drug_a] or required_gap > constraint_map[drug_a][drug_b]:
                constraint_map[drug_a][drug_b] = required_gap
                constraint_map[drug_b][drug_a] = required_gap
                
        return constraint_map

    def generate_schedule(
        self, 
        dosages: List[MedicationDosage], 
        interactions: List[InteractionRecord]
    ) -> Dict[str, Any]:
        """
        Calculates the optimized conflict-free daily timeline.
        
        Args:
            dosages: List of prescribed drugs and their daily frequencies.
            interactions: List of exact db constraints for this specific drug combination.
            
        Returns:
            JSON-serializable Schedule payload and explicit constraint notes.
        """
        constraint_map = self._build_constraint_graph(interactions)
        
        # Flatten the dosages into individual pills that need mapping
        # e.g., Aspirin (fre=2) -> ['ASPIRIN', 'ASPIRIN']
        pills_to_schedule = []
        for dosage in dosages:
            pills_to_schedule.extend([dosage.drug_name.upper()] * dosage.frequency)
            
        # We want to schedule the "hardest" medications first.
        # Heuristic: sort by the number of constraint edges they have in the graph.
        pills_to_schedule.sort(key=lambda d: len(constraint_map.get(d, {})), reverse=True)
        
        # Final timeline representation: SlotTime -> List[DrugNames]
        schedule_slots: Dict[int, List[str]] = {slot: [] for slot in self.AVAILABLE_SLOTS}
        
        notes = []
        
        # Greedy Constraint-Based Router
        for pill in pills_to_schedule:
            placed = False
            
            # Find the best valid slot
            for slot in self.AVAILABLE_SLOTS:
                valid_slot = True
                
                # Rule 1: Don't take two doses of the exact same medication at the exact same time
                if pill in schedule_slots[slot]:
                    continue
                    
                # Rule 2: Ensure doses of the *same* drug are spread out by at least 4 hours
                # If we take ASPIRIN at 8, don't take the second ASPIRIN at 10.
                same_drug_gap_violation = False
                for check_slot, placed_drugs in schedule_slots.items():
                    if pill in placed_drugs:
                        if abs(check_slot - slot) < 4:
                            same_drug_gap_violation = True
                            break
                if same_drug_gap_violation:
                    continue

                # Rule 3: Check temporal separation constraints against ALL other placed drugs
                for check_slot, placed_drugs in schedule_slots.items():
                    for placed_drug in placed_drugs:
                        # Is there a pharmacokinetic conflict rule between these two?
                        required_gap = constraint_map.get(pill, {}).get(placed_drug, 0)
                        
                        # Note: Contradicted drugs (24h gap) will simply fail to place entirely.
                        if required_gap > 0:
                            actual_gap = abs(check_slot - slot)
                            if actual_gap < required_gap:
                                valid_slot = False
                                break # Violates separation constraint, jump to next slot
                                
                    if not valid_slot:
                        break # Break outer loop, jump to next slot
                        
                if valid_slot:
                    schedule_slots[slot].append(pill)
                    placed = True
                    break # Move to next pill
            
            if not placed:
                notes.append(f"WARNING: Insufficient safe time slots to schedule '{pill}'. It violates rigid interaction separation windows or frequency caps. Please consult a physician to adjust dosage.")
        
        # Format the timeline output for the API contract
        formatted_schedule = []
        for time_slot in sorted(self.AVAILABLE_SLOTS):
            if schedule_slots[time_slot]:
                formatted_time_str = f"{time_slot:02d}:00"
                formatted_schedule.append({
                    "time": formatted_time_str,
                    "medications": schedule_slots[time_slot]
                })
                
        # Generate positive explanation notes if scheduling succeeded cleanly
        if not notes:
            for interaction in interactions:
                if interaction.severity in [SeverityLevel.SEVERE, SeverityLevel.MODERATE, SeverityLevel.CONTRAINDICATED]:
                    hours = self.SEPARATION_CONSTRAINTS[interaction.severity]
                    notes.append(f"Separated {interaction.drug_a} and {interaction.drug_b} by at least {hours} hours due to {interaction.severity.value} interaction risk.")
            if not notes:
                notes.append("No dangerous interactions detected. Standard spreading applied.")

        return {
            "schedule": formatted_schedule,
            "notes": " ".join(notes)
        }
