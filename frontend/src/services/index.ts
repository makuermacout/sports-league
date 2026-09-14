import { httpApi } from "./httpApi";
import { mockApi } from "./mockApi";
import type { LeagueApi } from "../types";

export function getApi(): LeagueApi {
  return import.meta.env.VITE_USE_MOCK === "false" ? httpApi : mockApi;
}

export { httpApi, mockApi };
