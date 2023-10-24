import React from "react";

const HomePage = () => {
  return (
    <div>
      <header>
        <h1>Welcome to the Collaborative Travel Planner</h1>
      </header>
      <main>
        <section>
          <h2>Plan Your Perfect Trip with Friends</h2>
          <p>
            Our app uses data science to create a personalized travel experience
            based on your group's preferences.
          </p>
        </section>
        <section>
          <h2>Key Features</h2>
          <ul>
            <li>Group Preferences Analysis</li>
            <li>Dynamic Itinerary Generation</li>
            <li>Expense Splitting and Budgeting</li>
            <li>Real-time Recommendations</li>
            <li>Weather and Event Integration</li>
          </ul>
        </section>
        <section>
          <p>Ready to get started?</p>
          <div>
            <button>Sign Up</button>
            <button>Log In</button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default HomePage;
