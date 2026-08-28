import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";

export default function RiskGauge({ score }) {
  const color = score >= 70 ? "#dc2626" : score >= 40 ? "#f59e0b" : "#16a34a";
  const data = [{ name: "risk", value: score, fill: color }];
  return (
    <RadialBarChart
      width={220}
      height={220}
      innerRadius={70}
      outerRadius={100}
      data={data}
      startAngle={90}
      endAngle={-270}
    >
      <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
      <RadialBar dataKey="value" cornerRadius={10} background clockWise />
      <text x={110} y={110} textAnchor="middle" fontSize={32} fontWeight="bold" fill={color}>
        {score}
      </text>
    </RadialBarChart>
  );
}
