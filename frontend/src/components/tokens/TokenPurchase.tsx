
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Coins, Check } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { toast } from '@/hooks/use-toast';

interface TokenPackage {
  id: string;
  tokens: number;
  price: number;
  popular?: boolean;
  bonus?: number;
}

const tokenPackages: TokenPackage[] = [
  {
    id: 'basic',
    tokens: 100,
    price: 4.99,
  },
  {
    id: 'popular',
    tokens: 500,
    price: 19.99,
    popular: true,
    bonus: 50,
  },
  {
    id: 'premium',
    tokens: 1000,
    price: 34.99,
    bonus: 200,
  },
];

export const TokenPurchase: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const { addTokens } = useAuthStore();

  const handlePurchase = async (pkg: TokenPackage) => {
    setIsProcessing(true);
    setSelectedPackage(pkg.id);

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const totalTokens = pkg.tokens + (pkg.bonus || 0);
      addTokens(totalTokens);
      
      toast({
        title: "Purchase Successful!",
        description: `${totalTokens} tokens have been added to your account.`,
      });
      
      setIsOpen(false);
    } catch (error) {
      toast({
        title: "Purchase Failed",
        description: "There was an error processing your payment. Please try again.",
      });
    } finally {
      setIsProcessing(false);
      setSelectedPackage(null);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="w-full bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 text-white">
          <Coins className="w-4 h-4 mr-2" />
          Buy Tokens
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl bg-background border-white/10">
        <DialogHeader>
          <DialogTitle className="text-white text-xl">Purchase Tokens</DialogTitle>
        </DialogHeader>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          {tokenPackages.map((pkg) => (
            <Card 
              key={pkg.id} 
              className={`relative glass-ultra border-white/10 bg-white/5 transition-all hover:border-white/20 ${
                pkg.popular ? 'border-yellow-500/50 ring-1 ring-yellow-500/20' : ''
              }`}
            >
              {pkg.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-yellow-500 to-orange-600 text-white text-xs px-3 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}
              <CardHeader className="text-center">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-500 to-orange-600 flex items-center justify-center mx-auto mb-3">
                  <Coins className="w-6 h-6 text-white" />
                </div>
                <CardTitle className="text-white">{pkg.tokens} Tokens</CardTitle>
                {pkg.bonus && (
                  <p className="text-green-400 text-sm">+ {pkg.bonus} bonus tokens</p>
                )}
                <div className="text-2xl font-bold text-white">${pkg.price}</div>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => handlePurchase(pkg)}
                  disabled={isProcessing}
                  className={`w-full ${
                    pkg.popular 
                      ? 'bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700' 
                      : 'bg-white/10 hover:bg-white/20'
                  } text-white`}
                >
                  {isProcessing && selectedPackage === pkg.id ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Processing...
                    </div>
                  ) : (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      Purchase
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
};
