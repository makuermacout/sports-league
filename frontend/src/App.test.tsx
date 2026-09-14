import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { createMockApi } from "./services/mockApi";
import { LeagueApiError } from "./types";
import type { LeagueApi } from "./types";

describe("App", () => {
  it("adds a team and shows it with zero standings", async () => {
    const user = userEvent.setup();
    render(<App api={createMockApi()} />);

    await user.type(screen.getByLabelText("Team name"), "Harbor United");
    await user.click(screen.getByRole("button", { name: "Add team" }));

    const row = await screen.findByRole("row", { name: /Harbor United/ });
    expect(row).toHaveTextContent("Harbor United");
    expect(row.textContent).toMatch(/0/);
    expect(screen.getByRole("list", { name: "Teams in the league" })).toHaveTextContent(
      "Harbor United",
    );
  });

  it("records a match and updates the log and table", async () => {
    const user = userEvent.setup();
    const api = createMockApi();
    const north = await api.createTeam("North End");
    const south = await api.createTeam("South Side");
    render(<App api={api} />);

    const home = await screen.findByLabelText("Home");
    await user.selectOptions(home, north.id);
    await user.selectOptions(screen.getByLabelText("Away"), south.id);
    await user.clear(screen.getByLabelText("Home score"));
    await user.type(screen.getByLabelText("Home score"), "2");
    await user.clear(screen.getByLabelText("Away score"));
    await user.type(screen.getByLabelText("Away score"), "1");
    await user.click(screen.getByRole("button", { name: "Record match" }));

    expect(await screen.findByText("North End vs South Side")).toBeInTheDocument();
    expect(screen.getByText("2–1")).toBeInTheDocument();
    expect(screen.getByRole("row", { name: /North End/ })).toHaveTextContent("3");
  });

  it("shows a fetch error without crashing when the backend is unreachable", async () => {
    const failing: LeagueApi = {
      listTeams: vi.fn().mockRejectedValue(
        new LeagueApiError("unreachable", "Cannot reach the scoreboard server."),
      ),
      createTeam: vi.fn(),
      listMatches: vi.fn(),
      createMatch: vi.fn(),
      getStandings: vi.fn(),
    };
    render(<App api={failing} />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Cannot reach the scoreboard server.",
    );
    expect(screen.getByRole("heading", { name: "Matchday Table" })).toBeInTheDocument();
  });
});

describe("createMockApi", () => {
  it("rejects duplicate team names", async () => {
    const api = createMockApi();
    await api.createTeam("River FC");
    await expect(api.createTeam("River FC")).rejects.toMatchObject({
      code: "duplicate_team",
    });
  });
});
