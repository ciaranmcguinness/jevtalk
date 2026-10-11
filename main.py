from typesafe_sdk import Choice, TypeSafeClient, Noul, ChoiceAnswer, NoulAnswer
from agents import function_tool, Agent, Runner, run_demo_loop, set_tracing_disabled, ModelSettings
from openai.types.shared import Reasoning
from agents.extensions.models.any_llm_provider import AnyLLMProvider
from dotenv import dotenv_values
from dataclasses import dataclass

set_tracing_disabled(True)

@dataclass
class Config():
    oai_base: str
    oai_key: str
    typesafe_base: str
    typesafe_key: str
    

def get_keys():
    env = dotenv_values()
    oai_base = env.get("OPENAI_BASE_URL")
    if oai_base == None:
        oai_base = "https://api.openai.com/v1"
    typesafe_base = env.get("TYPESAFE_BASE_URL")
    if typesafe_base == None:
        typesafe_base = "https://api.typesafe.ai/v1"
    oai_key = env.get("OPENAI_API_KEY")
    if oai_key == None:
        oai_key = input("Enter your OpenAI (or compatible) key: ")
    typesafe_key = env.get("TYPESAFE_API_KEY")
    if typesafe_key == None:
        typesafe_key = input("Enter your Typesafe (or compatible) key: ")
    return Config(oai_base,oai_key,typesafe_base,typesafe_key)

def run(inp, update, conf: Config):
    convo = inp.copy()
    r = Runner()
    p = AnyLLMProvider(api_key=conf.oai_key,base_url=conf.oai_base)
    agent = Agent("JevTalker", instructions="Write a list of options for the next word in the AI's message (up to ~20). Do not write more than one word per option. The AI is somewhat prone to looping, so steer away from things that have been said already. Do not allow the AI to respond as the user.", model=p.get_model("openrouter/openai/gpt-6-luna"), output_type=list[str], model_settings=ModelSettings(reasoning=Reasoning(effort="medium")))
    with TypeSafeClient(api_key=conf.typesafe_key,base_url=conf.typesafe_base) as typesafe:
        while True:
            choices = (r.run_sync(agent, str(convo))).final_output
            if choices == []:
                break
            nxt = typesafe.system_one(convo,{"next_token":Choice(criteria={k:"" for k in choices}, instructions="Pick the most likely next token for the AI to say in the conversation.")})
            assert isinstance(nxt.answers["next_token"],ChoiceAnswer)
            nxttoken = nxt.answers["next_token"].choice
            sp = " "
            if nxttoken in [",",".","?","!"]:
                sp = ""
            convo[-1]["content"]+= (nxttoken + sp)
            update(nxttoken)
            wc = len(convo[-1]["content"].split(" ")) - 1
            if (wc > 3):
                stop_req = typesafe.system_one({"message":convo[-2]["content"],"response":convo[-1]["content"]}, {"end":Noul(instructions="Should the response end here?")}).answers
                assert isinstance(stop_req["end"], NoulAnswer)
                stop_prob = stop_req["end"].noul
                stop_prob *= max(wc/8, min(wc/5, 1.25))
                if stop_prob > 0.5:
                    break
    return convo

def cli():
    conf = get_keys()
    convo = []
    while True:
        convo.append({"role":"user", "content":input(">")})
        convo.append({"role":"AI","content":""})
        convo = run(convo, lambda x: print(x, end=" ", flush=True), conf)
        print()

def main():
    cli()


if __name__ == "__main__":
    main()
