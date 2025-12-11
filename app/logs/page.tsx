import { redirect } from 'next/navigation'
import { getServerSession } from '@/lib/auth'
import SidebarLayout from '@/components/SidebarLayout'
import LogsClient from '@/components/LogsClient'

export default async function LogsPage() {
  const session = await getServerSession()
  
  if (!session || !session.user) {
    redirect('/login')
  }

  return (
    <SidebarLayout user={{ email: session.user.email || '', name: session.user.name }}>
      <LogsClient />
    </SidebarLayout>
  )
}
