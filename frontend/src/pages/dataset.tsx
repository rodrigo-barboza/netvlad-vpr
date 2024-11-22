import { useEffect, useState } from "react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@radix-ui/react-tabs";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

export default function Datasets() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [locations, setLocations] = useState<any>({});

  // Requisição para obter as localizações e arquivos
  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch("http://127.0.0.1:3000/locations");
        const data = await response.json();
        setLocations(data);
      } catch (error) {
        console.error("Error fetching locations:", error);
      }
    };

    fetchLocations();
  }, []);

  return (
    <div className="h-screen pt-2 pb-24 pl-2 pr-2 overflow-auto md:pt-0 md:pr-0 md:pl-0 flex flex-col">
      <Tabs className="w-full flex flex-col flex-grow">
        <TabsList className="flex space-x-4 mb-4 justify-center">
          {/* Botões para as categorias com fundo verde */}
          {Object.keys(locations).map((location) => (
            <TabsTrigger
              key={location}
              value={location}
              className="px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600"
            >
              {location}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* Conteúdo das abas com flex-grow */}
        {Object.keys(locations).map((location) => (
          <TabsContent
            key={location}
            value={location}
            className="flex flex-col flex-grow w-full"
          >
            <Card className="flex flex-col flex-grow w-full">
              <CardHeader>
                <CardTitle>Imagens de {location}</CardTitle>
                <CardDescription>
                  Lista de imagens usadas no treinamento correspondentes a{" "}
                  {location}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col flex-grow w-full overflow-auto">
                <div className="grid grid-cols-4 gap-4 h-full">
                  {locations[location].map((filename: string) => (
                    <img
                      key={filename}
                      className="w-full h-auto object-cover rounded-sm"
                      src={`/dataset/${filename}`}
                      alt={filename}
                    />
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
