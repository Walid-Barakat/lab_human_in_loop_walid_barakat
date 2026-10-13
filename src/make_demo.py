"""Synthetic candidates and synthetic reference scores, never human annotations."""
from pathlib import Path
import json,random
ROOT=Path(__file__).resolve().parents[1]

# Each answer is deliberately authored for teaching. Tests shown here are
# reference cases, not fabricated execution results. Units/contracts are explicit.
TASKS=[
('E01','energy_units','Write kwh_to_mwh(kwh): convert a nonnegative numeric kWh value to MWh. Raise ValueError for negative input. Include a docstring and normal/edge examples.',
 '1000 -> 1.0; 0 -> 0.0; -1 -> ValueError. 1 MWh = 1000 kWh.',
 'def kwh_to_mwh(kwh):\n    return kwh * 1000',
 'def kwh_to_mwh(kwh):\n    """Convert nonnegative kWh to MWh; negative energy is invalid."""\n    if kwh < 0:\n        raise ValueError("kwh must be nonnegative")\n    return kwh / 1000\n\n# kwh_to_mwh(1000) -> 1.0\n# kwh_to_mwh(0) -> 0.0\n# kwh_to_mwh(-1) raises ValueError',
 (0,0,0,'correctness','Multiplication reverses the required conversion: 1000 kWh would return 1000000 instead of 1 MWh.'),
 (3,2,2,'none','The code divides by 1000, preserves zero and explicitly rejects negative input; examples cover normal and edge cases.')),
('E02','mean_load','Write mean_load(values) for a nonempty list of nonnegative numeric kW samples. Reject an empty list or negative sample with ValueError. Include a docstring and two examples.',
 '[2,4] -> 3.0; [0] -> 0.0; [] or [-1,2] -> ValueError.',
 'def mean_load(values):\n    return sum(values) / len(values)\n\n# mean_load([2, 4]) -> 3.0',
 'def mean_load(values):\n    """Return mean kW load; empty or negative samples raise ValueError."""\n    if not values or any(v < 0 for v in values):\n        raise ValueError("nonempty nonnegative samples required")\n    return sum(values) / len(values)\n\n# mean_load([2, 4]) -> 3.0\n# mean_load([]) raises ValueError',
 (1,0,1,'missing_validation','Ordinary arithmetic is correct, but the empty case raises the wrong exception and negative samples are accepted.'),
 (3,2,2,'none','Both specified invalid cases are rejected; normal and empty-list examples state expected behavior.')),
('E03','peak_load','Write peak_load(values): max of a nonempty list of nonnegative kW readings. Raise ValueError for empty or negative readings. Add docs and normal/edge examples.',
 '[2,7,3] -> 7; [0] -> 0; [] and [-1] -> ValueError.',
 'def peak_load(values):\n    """Peak kW, requiring nonempty nonnegative values."""\n    if not values or any(v < 0 for v in values):\n        raise ValueError("invalid readings")\n    return max(values)\n\n# peak_load([2, 7, 3]) -> 7\n# peak_load([]) raises ValueError',
 'def peak_load(values):\n    return values[0]',
 (3,2,2,'none','The maximum and both invalid cases match the contract; examples include an ordinary and an empty-list case.'),
 (0,0,0,'correctness','Returns the first reading rather than the peak; [2,7,3] would return 2.')),
('E04','capacity_factor','Write capacity_factor(actual_kwh, rated_kw, hours): actual/(rated*hours). Require rated_kw>0, hours>0, and actual_kwh>=0; otherwise ValueError. Do not clamp values above1. Add docs and examples.',
 '(50,10,10) -> 0.5; (0,10,10) -> 0; (1,0,1) -> ValueError; (120,10,10) -> 1.2.',
 'def capacity_factor(actual_kwh, rated_kw, hours):\n    return actual_kwh / rated_kw\n\n# capacity_factor(50, 10, 10) -> 5',
 'def capacity_factor(actual_kwh, rated_kw, hours):\n    """Ratio of actual kWh to rated kW times hours; no clamping."""\n    if actual_kwh < 0 or rated_kw <= 0 or hours <= 0:\n        raise ValueError("invalid energy, capacity or duration")\n    return actual_kwh / (rated_kw * hours)\n\n# capacity_factor(50, 10, 10) -> 0.5\n# capacity_factor(1, 0, 1) raises ValueError',
 (0,0,0,'correctness','The denominator omits hours. The example confirms a result inconsistent with the requested ratio.'),
 (3,2,2,'none','Units, denominator, invalid inputs and the no-clamping rule are explicit.')),
('E05','battery_runtime','Write battery_runtime(usable_kwh, load_kw): hours at constant load, usable/load. Require usable>=0 and load>0; ValueError otherwise. Add docs and examples. Treat usable energy as already derated.',
 '(20,5) -> 4; (0,5) -> 0; (20,0) -> ValueError. Do not add efficiency or reserve assumptions.',
 'def battery_runtime(usable_kwh, load_kw):\n    if load_kw <= 0 or usable_kwh < 0:\n        raise ValueError("invalid input")\n    return usable_kwh / load_kw',
 'def battery_runtime(usable_kwh, load_kw):\n    """Runtime hours at constant kW load using already-usable kWh."""\n    if usable_kwh < 0 or load_kw <= 0:\n        raise ValueError("usable >=0 and load >0 required")\n    return usable_kwh / load_kw\n\n# battery_runtime(20, 5) -> 4.0\n# battery_runtime(0, 5) -> 0.0',
 (3,0,0,'mixed','The functional contract is met, but the requested docstring and examples are absent.'),
 (3,2,2,'none','No extra derating is invented; docstring and normal/zero-energy examples match the contract.')),
('E06','tariff_cost','Write tariff_cost(kwh, euro_per_kwh): product of two nonnegative numbers; ValueError for negative input. Include a docstring and normal/edge examples; no tax assumptions.',
 '(100,0.3) -> 30; (0,0.3) -> 0; (-1,0.3) -> ValueError.',
 'def tariff_cost(kwh, euro_per_kwh):\n    """Cost in EUR: nonnegative kWh times nonnegative EUR/kWh."""\n    if kwh < 0 or euro_per_kwh < 0:\n        raise ValueError("negative inputs")\n    return kwh * euro_per_kwh\n\n# tariff_cost(100, 0.3) -> 30.0\n# tariff_cost(-1, 0.3) raises ValueError',
 'def tariff_cost(kwh, euro_per_kwh):\n    """Multiply energy by tariff."""\n    return kwh * euro_per_kwh\n\n# tariff_cost(100, 0.3) -> 30.0',
 (3,2,2,'none','The tariff units and negative-input behavior are stated; examples include a normal and invalid case.'),
 (1,1,1,'missing_validation','Correct ordinary product, but both negative-input checks are absent; docs and examples are partial.')),
('E07','threshold_count','Write count_above(values, threshold) for numeric inputs: count readings strictly greater than threshold. Empty list returns0. Include a docstring and normal/edge examples.',
 '([1,2,3],2) -> 1; ([],2) -> 0; ([2],2) -> 0. Equality must not count.',
 'def count_above(values, threshold):\n    return sum(v >= threshold for v in values)\n\n# count_above([1, 2, 3], 2) -> 2',
 'def count_above(values, threshold):\n    """Count readings strictly above threshold; empty lists return zero."""\n    return sum(v > threshold for v in values)\n\n# count_above([1, 2, 3], 2) -> 1\n# count_above([2], 2) -> 0',
 (1,0,0,'correctness','Uses greater-or-equal, failing the central threshold boundary; the shown expected output is wrong for the prompt.'),
 (3,2,2,'none','Strict comparison and equality example match the boundary requirement; empty sum naturally returns zero.')),
('E08','pue','Write pue(total_kwh, it_kwh): total/IT. Require IT>0 and total>=IT; ValueError otherwise. Add a docstring and normal/edge examples. This is an arithmetic helper, not engineering approval.',
 '(120,100) -> 1.2; (100,100) -> 1; (80,100) or (1,0) -> ValueError.',
 'def pue(total_kwh, it_kwh):\n    """Ratio of total to IT energy; IT>0 and total>=IT."""\n    if it_kwh <= 0 or total_kwh < it_kwh:\n        raise ValueError("invalid energy balance")\n    return total_kwh / it_kwh\n\n# pue(120, 100) -> 1.2\n# pue(80, 100) raises ValueError',
 'def pue(total_kwh, it_kwh):\n    return it_kwh / total_kwh',
 (3,2,2,'none','The ratio and validation follow the supplied contract; examples include an invalid energy balance.'),
 (0,0,0,'correctness','Inverts the ratio: (120,100) returns about0.833 instead of1.2.')),
('E09','percentage_change','Write percentage_change(old,new): (new-old)/old*100. Require old>0 and new>=0; ValueError otherwise. Add docstring and normal/edge examples.',
 '(100,120) -> 20; (100,0) -> -100; (0,1) -> ValueError.',
 'def percentage_change(old, new):\n    """Percent change relative to positive old value; new must be nonnegative."""\n    if old <= 0 or new < 0:\n        raise ValueError("invalid baseline or new value")\n    return (new - old) / old * 100\n\n# percentage_change(100, 120) -> 20.0\n# percentage_change(100, 0) -> -100.0',
 'def percentage_change(old, new):\n    """Percent change from old to new."""\n    return (new - old) / old * 100\n\n# percentage_change(100, 120) -> 20.0',
 (3,2,2,'none','Formula and validation match the specified baseline and zero-new-value behavior.'),
 (1,1,1,'missing_validation','The ordinary formula works, but old0 raises ZeroDivisionError instead of ValueError; invalid inputs are undocumented.')),
('E10','load_factor','Write load_factor(values): mean/peak for a nonempty list of nonnegative loads. Return0 if all values are0; reject empty/negative input with ValueError. Add docs and examples.',
 '[2,4] -> 0.75; [0,0] -> 0; [] and [-1,2] -> ValueError.',
 'def load_factor(values):\n    """Mean-to-peak ratio; empty/negative loads are invalid."""\n    if not values or any(v < 0 for v in values):\n        raise ValueError("invalid loads")\n    peak = max(values)\n    return 0 if peak == 0 else (sum(values) / len(values)) / peak\n\n# load_factor([2, 4]) -> 0.75\n# load_factor([0, 0]) -> 0',
 'def load_factor(values):\n    # mean divided by peak\n    return sum(values) / len(values) / max(values)\n\n# load_factor([2, 4]) -> 0.75',
 (3,2,2,'none','Handles the required all-zero edge case as0 and rejects invalid inputs, with useful examples.'),
 (1,1,1,'missing_validation','All-zero loads divide by zero; empty/negative input is not handled. Comment and ordinary example are only partial documentation.')),
]

def generate_demo():
 records=[];fixtures=[]
 for pid,topic,instruction,validation,a,b,sa,sb in TASKS:
  for alias,answer,score in [('candidate_A',a,sa),('candidate_B',b,sb)]:
   rid=f'{pid}-{alias[-1]}'
   row=dict(record_id=rid,prompt_id=pid,candidate_alias=alias,topic=topic,
       data_origin='synthetic_authored_demo',instruction=instruction,
       response='```python\n'+answer+'\n```',validation_context=validation)
   records.append(row)
   quality,docs,examples,issue,comment=score
   values={'code_quality':quality,'documentation':docs,'examples':examples,
       'primary_issue':issue,'evaluation_confidence':'high','comment':comment}
   fixtures.append({'record_id':rid,'fields':{f:row[f] for f in ['instruction','response','validation_context']},
      'metadata':{f:row[f] for f in ['prompt_id','candidate_alias','topic','data_origin']},
      'responses':[{'question_name':k,'value':v,'user_id':'synthetic_reference_fixture',
                    'status':'submitted'} for k,v in values.items()],
      'annotation_source':'synthetic_reference_not_human','exported_at':'2026-10-10T00:00:00Z'})
 random.Random(91).shuffle(records)
 folder=ROOT/'data/demo';folder.mkdir(parents=True,exist_ok=True)
 (folder/'evaluation_records.json').write_text(json.dumps(records,indent=2)+'\n')
 (folder/'reference_annotation_fixture.json').write_text(json.dumps(fixtures,indent=2)+'\n')
 return records,fixtures

if __name__=='__main__':generate_demo()
