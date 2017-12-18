#!/usr/bin/env python2.7
# 15/12/2017 version 1.0 by Jackie Chen
# - Add feature to search user status in AD and Crowd
# - Add feature to disable users in Crowd if they were disabled in AD

import crowd
import ad
import params
import sys
import json
import argparse


def get_user(user):
  userinfo = {}
  usermeta = mycrowd.get_user(username=user)
  if usermeta['status']:
    userinfo['name'] = usermeta['user']['name']
    userinfo['display-name'] = usermeta['user']['display-name']
    userinfo['active'] = usermeta['user']['active']
    userinfo['email'] = usermeta['user']['email'] if 'email' in usermeta['user'] else ' '
    userinfo['first-name'] = usermeta['user']['first-name']
    userinfo['last-name'] = usermeta['user']['last-name']
    print userinfo
    return userinfo
  else:
    print user + " is not found in Crowd."
    return False


def get_active_users():
  users = []
  for user in mycrowd.get_user(username='all')['users']:
    users.append(user['name'])
  print "There are " + str(len(users)) + " active users in Crowd."
  return users


def disable_user(user):
  print '---Before-------------:'
  userinfo = get_user(user)
  userinfo['active'] = 'false'
  mycrowd.update_user(username=user, data=userinfo)
  print '---After-------------:'
  get_user(user)
  print ' '


def enable_user(user):
  print '---Before-------------:'
  userinfo = get_user(user)
  userinfo['active'] = 'true'
  mycrowd.update_user(username=user, data=userinfo)
  print '---After-------------:'
  get_user(user)
  print ' '


def user_ad_status(user, msg='on'):
  result = myad.search_user(params.ad['base'], user)
  if result:
    if msg == 'on':
      print result
    return result[0].userAccountControl 
  else:
    if msg == 'on':
      print user + " is not found in AD."
    return False      


def sync_user(readonly='no'):
  users = get_active_users()
  for user in users:
    flag = str(user_ad_status(user, 'off'))
    if flag in ['514', '546', '66050']:
      print user + ' was already disabled in Active Directory. flag:' + flag
      if readonly != 'yes':
        print 'Disable ' + user + ' in Crowd.'
        disable_user(user)


def check_ad_user(user):
  '''
  512 Enabled Account
  514 Disabled Account
  544 Enabled, Password Not Required
  546 Disabled, Password Not Required
  66048 Enabled, Password Doesn't Expire
  66050 Disabled, Password Doesn't Expire
  66080 Enabled, Password Doesn't Expire & Not Required
  66082 Disabled, Password Doesn't Expire & Not Required
  '''
  user_in_ad = user_ad_status(user)
  if user_in_ad:
      if str(user_in_ad) in ['514', '546', '66050', '66082']:
        print '>>>>>> ' + user + ' is disabled in Active Directory.'   
      else:
        print '>>>>>> ' + user + ' is active in Active Directory.' 
  user_in_crowd = get_user(user)         
  if user_in_crowd:
    if user_in_crowd['active'] == 'False':
      print '>>>>>> ' + user + ' is disabled in Crowd.'
    else:    
      print '>>>>>> ' + user + ' is active in Crowd.'


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-a', '--active', help='show all active users in Crowd', action='store_true')
  parser.add_argument('-c', '--compare', metavar='username', help='compare a user in AD and Crowd')  
  parser.add_argument('-d', '--disable', metavar='username', help='disable a use in Crowd')
  parser.add_argument('-e', '--enable', metavar='username', help='enable a user in Crowd')
  parser.add_argument('-r', '--report', help='report mode of synchronize, work with -sync', action='store_true')
  parser.add_argument('--search-ad', metavar='username', help='search a user status in AD')
  parser.add_argument('--search-crowd', metavar='username', help='search a user in Crowd')
  parser.add_argument('-sync', '--synchronize', help='synchronize disabled user in AD to Crowd', action='store_true')


  args = parser.parse_args()
  if args.active:
    get_active_users()
  if args.compare:
    check_ad_user(args.compare)   
  if args.disable:
    disable_user(args.disable)
  if args.enable:
    enable_user(args.enable)
  if args.search_ad:
    user_ad_status(args.search_ad)
  if args.search_crowd:
    get_user(args.search_crowd)
  if args.synchronize:
    if args.report:
      sync_user('yes')
    else:
      sync_user()


if __name__ == '__main__':
  mycrowd = crowd.client(api_url=params.crowd['api_url'], app_name=params.crowd['app_name'], app_password=params.crowd['app_password'])
  myad = ad.client(server=params.ad['server'], username=params.ad['username'], password=params.ad['password'])
  main()
                            