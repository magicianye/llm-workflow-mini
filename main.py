from typing import Callable, Dict, List
from dataclasses import dataclass, field

@dataclass
class Step:
    name: str
    func: Callable[[dict], str]
    needs: List[str] = field(default_factory=list)

class Workflow:
    def __init__(self):
        self.steps: Dict[str, Step] = {}

    def add(self, step: Step):
        self.steps[step.name] = step
        return self

    def run(self, ctx=None):
        ctx = ctx or {}
        done = set()
        while len(done) < len(self.steps):
            ready = [s for s in self.steps.values() if s.name not in done and all(n in done for n in s.needs)]
            if not ready:
                raise ValueError('cycle or missing dependency')
            for step in ready:
                ctx[step.name] = step.func(ctx)
                done.add(step.name)
                print(f'[done] {step.name}: {ctx[step.name]}')
        return ctx

def mock_llm(prompt: str) -> str:
    return f'LLM({prompt[:40]}...)'

def main():
    wf = Workflow()
    wf.add(Step('extract', lambda ctx: 'user wants a weekly report'))
    wf.add(Step('plan', lambda ctx: mock_llm('Plan: ' + ctx['extract']), ['extract']))
    wf.add(Step('draft', lambda ctx: mock_llm('Draft: ' + ctx['plan']), ['plan']))
    wf.add(Step('review', lambda ctx: 'approved:' + ctx['draft'][:20], ['draft']))
    result = wf.run()
    print('\nFinal context:')
    for k, v in result.items():
        print(f'- {k}: {v}')

if __name__ == '__main__':
    main()