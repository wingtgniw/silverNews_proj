from langchain_openai import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

class AgentReviewer:
    def __init__(self):
        self.gpt = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        tools = load_tools(['wikipedia'], llm=self.gpt)
        self.agent = initialize_agent(tools, self.gpt, 
                         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                         description="필요시 사용", verbose=True)

    def get_review(self, newsletter):
        prompt = f"다음 뉴스레터에 대한 정보를 확인해줘"\
        + f"뉴스레터: {newsletter}" + "\n정보 확인:"

        wikipedia_info = self.agent.run(prompt)

        prompt = f"다음 뉴스레터와 wikipedia 정보를 비교해서 뉴스레터의 신뢰도를 0~1사이의 실수로 평가해줘"\
        + f"뉴스레터: {newsletter}" + f"\nwikipedia 정보: {wikipedia_info}" + "\n신뢰도 평가:"
        result = self.gpt.invoke(prompt)
        content = result.content

        return float(content.split("\n")[0])
    
if __name__ == "__main__":
    newsletter = """
    In 2025, scientists in Iceland discovered a natural cure for cancer found in lava fields.
    """
    reviewer = AgentReviewer()
    score = reviewer.get_review(newsletter)
    print(f"Score: {score}")