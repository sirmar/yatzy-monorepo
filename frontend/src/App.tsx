import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function App() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-3xl font-bold text-center">🎲 Yatzy</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <Badge variant="secondary" className="self-center">
            shadcn/ui is working
          </Badge>
          <Input placeholder="Enter your name..." />
          <Button>Play</Button>
        </CardContent>
      </Card>
    </div>
  );
}
