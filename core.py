from typesafe_sdk import Choice, TypeSafeClient, Noul, ChoiceAnswer, NoulAnswer
from agents import TResponseInputItem, function_tool, Agent, Runner, run_demo_loop, set_tracing_export_api_key, ModelSettings
from openai.types.shared import Reasoning
from agents.extensions.models.any_llm_provider import AnyLLMProvider
from dotenv import dotenv_values
from dataclasses import dataclass
from copy import deepcopy


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

def get_jev_choice_and_quit(choices: list[str], convo, conf: Config):
    with TypeSafeClient(api_key=conf.typesafe_key,base_url=conf.typesafe_base) as typesafe:
        nxt = typesafe.system_one(convo,{"next_token":Choice(criteria={k:"" for k in choices}, instructions="Pick the most likely next token for the AI to say in the conversation.")})
        assert isinstance(nxt.answers["next_token"],ChoiceAnswer)
        nxttoken = nxt.answers["next_token"].choice
        sp = " "
        if nxttoken in [",",".","?","!"]:
            sp = ""
        nxttoken = sp + nxttoken  
        wc = len(convo[-1]["content"].split(" ")) - 1
        stop_req = typesafe.system_one({"message":convo[-2]["content"],"response":convo[-1]["content"] + nxttoken}, {"end":Noul(instructions="Should the AI's response end here?")}).answers
        assert isinstance(stop_req["end"], NoulAnswer)
        stop_prob = stop_req["end"].noul
        stop_prob *= 0.90+wc/16
        if stop_prob > 0.5:
            return True, nxttoken
        return False, nxttoken
    

def run(inp: list[dict[str,str]], update, conf: Config):
    convo = deepcopy(inp)
    convo.append({"role":"AI","content":""})
    r = Runner()
    p = AnyLLMProvider(api_key=conf.oai_key,base_url=conf.oai_base,api="chat_completions")
    agent = Agent("JevTalker", instructions="Write a list of options for the next word in the AI's message (up to ~50), the words should provide a wide palet for the AI, focus more on providing options with different meanings rather than providing multiple ways to say the same thing. The AI is not able to write its own punctuation, so you'll need to provide it. Do not write more than one word per option. The AI is somewhat prone to looping, so steer away from things that have been said already. Prevent the AI to respond as the user, it it is responding as the user, steer it away from that.", model=p.get_model("openrouter/openai/gpt-6-luna"), output_type=list[str], model_settings=ModelSettings(reasoning=Reasoning(effort="medium")))
    state: list[TResponseInputItem] = [{"role":"user","content":f"The following is the conversation's starting context:{convo}"}]
    while True:
        resp = (r.run_sync(agent, state))
        choices = resp.final_output + ["!"]
        state = resp.to_input_list()
        print(state)
        if choices == []:
            break
        stop, nxt = get_jev_choice_and_quit(choices, convo, conf)
        update(nxt)
        if stop:
            break
        convo[-1]["content"] += nxt
        state.append({"role":"assistant","content":f"The AI picked \"{nxt}\" as the next token."})

    return convo