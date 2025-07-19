import React from 'react';
import { User } from '@/store/authStore';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Edit3, Crown } from 'lucide-react';
import { Link } from 'react-router-dom';
interface ProfileSectionProps {
  user: User | null;
}
export const ProfileSection: React.FC<ProfileSectionProps> = ({
  user
}) => {
  if (!user) return null;
  const getSubscriptionBadge = () => {
    switch (user.subscription) {
      case 'pro':
        return <Badge className="bg-gradient-to-r from-purple-500 to-blue-500">Pro</Badge>;
      case 'enterprise':
        return <Badge className="bg-gradient-to-r from-gold-500 to-yellow-500"><Crown className="w-3 h-3 mr-1" />Enterprise</Badge>;
      default:
        return <Badge variant="secondary">Free</Badge>;
    }
  };
  return (
    <div className="flex items-center gap-4 p-4 bg-card rounded-lg border">
      <Avatar className="h-16 w-16">
        <AvatarImage src={user.avatar} alt={user.name} />
        <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
      </Avatar>
      
      <div className="flex-1">
        <h3 className="font-semibold text-lg">{user.name}</h3>
        <p className="text-muted-foreground">{user.email}</p>
        <div className="mt-2">
          {getSubscriptionBadge()}
        </div>
      </div>
      
      <Button asChild variant="outline" size="sm">
        <Link to="/settings">
          <Edit3 className="h-4 w-4 mr-2" />
          Edit Profile
        </Link>
      </Button>
    </div>
  );
};