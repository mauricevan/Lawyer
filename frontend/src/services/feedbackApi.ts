import type { FeedbackCategory, FeedbackRequest } from "@/models/types";
import { getApiUrl } from "@/services/apiClient";

const API_URL = getApiUrl();

export async function submitFeedback(payload: FeedbackRequest): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Feedback failed: ${response.status}`);
  }
}

export const FEEDBACK_CATEGORIES: { id: FeedbackCategory; label: string; rating: number }[] = [
  { id: "incorrect", label: "Onjuist", rating: 1 },
  { id: "incomplete", label: "Onvolledig", rating: 2 },
  { id: "source_issue", label: "Bronprobleem", rating: 2 },
  { id: "ux", label: "Gebruiksvriendelijkheid", rating: 3 },
];
