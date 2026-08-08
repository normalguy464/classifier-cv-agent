import { NextResponse } from "next/server";

import { listDemoCases } from "@/lib/server/demo-cases";

export async function GET(): Promise<NextResponse> {
  return NextResponse.json(listDemoCases());
}
