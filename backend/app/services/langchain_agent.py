from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import Transaction, Budget, User
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

load_dotenv()

class FinanceAgent:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency, can be changed to gpt-4o or gpt-4-turbo
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent to use"""
        
        def get_transaction_summary(timeframe: str = "30") -> str:
            """Get summary of transactions for the last N days. Input should be number of days as string."""
            try:
                days = int(timeframe)
                start_date = datetime.utcnow() - timedelta(days=days)
                transactions = self.db.query(Transaction).filter(
                    Transaction.user_id == self.user.id,
                    Transaction.date >= start_date,
                    Transaction.is_pending == False
                ).all()
                
                total = sum(t.amount for t in transactions)
                by_category = {}
                for t in transactions:
                    category = t.category or "Uncategorized"
                    by_category[category] = by_category.get(category, 0) + abs(t.amount)
                
                summary = f"Total spending: ${total:.2f} over {days} days\n"
                summary += "By category:\n"
                for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                    summary += f"  {cat}: ${amount:.2f}\n"
                
                return summary
            except Exception as e:
                return f"Error: {str(e)}"
        
        def get_budget_status() -> str:
            """Get current budget status for all active budgets."""
            budgets = self.db.query(Budget).filter(
                Budget.user_id == self.user.id,
                Budget.is_active == True
            ).all()
            
            if not budgets:
                return "No active budgets found."
            
            status = "Budget Status:\n"
            for budget in budgets:
                percentage = (budget.current_spending / budget.monthly_limit * 100) if budget.monthly_limit > 0 else 0
                remaining = budget.monthly_limit - budget.current_spending
                status += f"{budget.category}: ${budget.current_spending:.2f} / ${budget.monthly_limit:.2f} ({percentage:.1f}%)\n"
                status += f"  Remaining: ${remaining:.2f}\n"
            
            return status
        
        def get_category_spending(category: str) -> str:
            """Get spending for a specific category. Input should be the category name."""
            start_date = datetime.utcnow() - timedelta(days=30)
            transactions = self.db.query(Transaction).filter(
                Transaction.user_id == self.user.id,
                Transaction.category == category,
                Transaction.date >= start_date,
                Transaction.is_pending == False
            ).all()
            
            total = sum(abs(t.amount) for t in transactions)
            count = len(transactions)
            avg = total / count if count > 0 else 0
            
            return f"Category: {category}\nTotal: ${total:.2f}\nTransactions: {count}\nAverage: ${avg:.2f}"
        
        def suggest_budget(category: str, current_spending: str) -> str:
            """Suggest a budget for a category based on current spending. Inputs: category name, current spending amount as string."""
            try:
                spending = float(current_spending)
                # Suggest 20% more than current spending as a reasonable budget
                suggested = spending * 1.2
                return f"Suggested budget for {category}: ${suggested:.2f} per month (based on current spending of ${spending:.2f})"
            except Exception as e:
                return f"Error: {str(e)}"
        
        tools = [
            Tool(
                name="get_transaction_summary",
                func=get_transaction_summary,
                description="Get a summary of transactions for the last N days. Input should be number of days as a string."
            ),
            Tool(
                name="get_budget_status",
                func=get_budget_status,
                description="Get the current status of all active budgets."
            ),
            Tool(
                name="get_category_spending",
                func=get_category_spending,
                description="Get spending details for a specific category. Input should be the category name."
            ),
            Tool(
                name="suggest_budget",
                func=suggest_budget,
                description="Suggest a budget amount for a category based on current spending. Inputs: category name, current spending amount as string."
            )
        ]
        
        return tools
    
    def _create_agent(self):
        """Create the LangChain agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful personal finance assistant. You help users understand their spending, 
            manage budgets, and make better financial decisions. Use the available tools to get real data 
            before making recommendations. Be conversational, helpful, and provide actionable advice."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        
        return agent_executor
    
    def chat(self, message: str) -> str:
        """Process a chat message and return a response"""
        try:
            result = self.agent.invoke({"input": message})
            return result.get("output", "I'm sorry, I couldn't process that request.")
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try rephrasing your question."

