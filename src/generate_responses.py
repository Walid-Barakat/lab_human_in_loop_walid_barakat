"""Optional real LLM responses. Requires user credentials and incurs API cost."""
from pathlib import Path
import os,json,random
from datetime import datetime,timezone
from dotenv import load_dotenv
from .make_demo import TASKS
from .workflow import ROOT,write_json


def main():
    from openai import OpenAI
    load_dotenv()
    if not os.getenv('OPENAI_API_KEY'):raise ValueError('Set OPENAI_API_KEY locally to generate actual responses.')
    client=OpenAI(timeout=60,max_retries=2)
    records=[];audit=[];failures=[]
    for pid,topic,instruction,validation,*_ in TASKS:
        for alias in ['candidate_A','candidate_B']:
            model=os.getenv('OPENAI_MODEL_'+alias[-1], 'gpt-4o-mini')
            system=('Answer the Python programming task accurately with the requested documentation and examples.'
                if alias=='candidate_A' else
                'Answer the Python programming task accurately. Check units and boundaries before writing; explicitly verify the requested validation, docstring and examples.')
            rid=f'{pid}-{alias[-1]}'
            try:
                response=client.chat.completions.create(model=model,temperature=0,max_completion_tokens=1500,
                    messages=[{'role':'system','content':system},{'role':'user','content':instruction}])
                choice=response.choices[0]
                if choice.finish_reason!='stop' or not choice.message.content:raise ValueError('Incomplete or empty model answer.')
                records.append(dict(record_id=rid,prompt_id=pid,candidate_alias=alias,topic=topic,
                    data_origin='openai_generated',instruction=instruction,response=choice.message.content,
                    validation_context=validation))
                audit.append(dict(record_id=rid,model=model,system_prompt=system,temperature=0,
                    generated_at=datetime.now(timezone.utc).isoformat(),provider_response_id=response.id,
                    usage=response.usage.model_dump() if response.usage else None))
            except Exception as exc:
                failures.append(dict(record_id=rid,error_type=type(exc).__name__))
            # Save completed results after each request; never fabricate missing answers.
            write_json(ROOT/'data/live/evaluation_records.json',records)
            write_json(ROOT/'data/live/model_generation_audit.json',audit)
            write_json(ROOT/'data/live/generation_failures.json',failures)
            print('Completed',len(records),'responses; failures',len(failures))
    random.Random(91).shuffle(records)
    write_json(ROOT/'data/live/evaluation_records.json',records)
    print('Generated records:',len(records),'of20. No annotations were created.')
    if failures:raise SystemExit('Some responses failed; review generation_failures.json before upload. A rerun generates new responses and replaces these local files; use a new Argilla dataset for changed content.')

if __name__=='__main__':main()
