from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

class AgentReviewer:
    def __init__(self):
        gpt = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        tools = load_tools(['wikipedia'], llm=gpt)
        self.agent = initialize_agent(tools, gpt, 
                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                         description="필요시 사용", verbose=True)

    def get_review(self, newsletter):
        prompt = f"다음 뉴스레터에 대한 신뢰도를 0~1사이의 실수로 표현해줘"\
        + f"뉴스레터: {newsletter}" + "\n신뢰도 점수:"

        return float(self.agent.run(prompt))
    
if __name__ == "__main__":
    newsletter = """
    In 2025, scientists in Iceland discovered a natural cure for cancer found in lava fields.
    """
    reviewer = AgentReviewer()
    score = reviewer.get_review(newsletter)
    print(f"Score: {score}")

