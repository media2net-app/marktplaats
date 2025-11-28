import { redirect } from 'next/navigation'
import { getServerSession } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import DashboardClient from '@/components/DashboardClient'
import SidebarLayout from '@/components/SidebarLayout'

export default async function DashboardPage() {
  const session = await getServerSession()
  
  if (!session || !session.user) {
    redirect('/login')
  }

  const products = await prisma.product.findMany({
    where: { userId: session.user.id },
    orderBy: { createdAt: 'desc' },
    include: {
      category: true,
    },
  })

  return (
    <SidebarLayout user={{ email: session.user.email || '', name: session.user.name }}>
      <DashboardClient products={products} />
    </SidebarLayout>
  )
}

